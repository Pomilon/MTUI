import os
import sys
import platform
import subprocess
import shutil
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        # Try to find cmake
        cmake_bin = shutil.which('cmake')
        
        # If not in path, try the python package
        if not cmake_bin:
            try:
                import cmake
                cmake_bin = os.path.join(cmake.CMAKE_BIN_DIR, 'cmake')
            except ImportError:
                pass
        
        if not cmake_bin:
            raise RuntimeError("CMake must be installed to build RC-TUI")

        for ext in self.extensions:
            self.build_extension(ext, cmake_bin)

    def build_extension(self, ext, cmake_bin):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        if not os.path.exists(extdir):
            os.makedirs(extdir)

        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DCMAKE_RUNTIME_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}'
        ]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        # Ninja is preferred for performance and stability in CI
        if shutil.which('ninja'):
            cmake_args += ['-GNinja']
        
        if platform.system() == "Windows":
            # On Windows, we need to ensure the DLL/PYD ends up in the right place
            # even if CMake uses a multi-config generator (like VS)
            for config_type in ['Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel']:
                cmake_args += [f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{config_type.upper()}={extdir}']
                cmake_args += [f'-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{config_type.upper()}={extdir}']
            
            if sys.maxsize > 2**32 and not shutil.which('ninja'):
                cmake_args += ['-A', 'x64']
        elif platform.system() == "Darwin":
            cmake_args += [f'-DCMAKE_BUILD_TYPE={cfg}']
            # Forward macOS architecture flags
            macosx_archs = os.environ.get("ARCHFLAGS")
            if macosx_archs:
                archs = [a for a in macosx_archs.split() if a not in ("-arch",)]
                cmake_args.append(f'-DCMAKE_OSX_ARCHITECTURES={";".join(archs)}')
            
            # Forward deployment target
            deployment_target = os.environ.get("MACOSX_DEPLOYMENT_TARGET")
            if deployment_target:
                cmake_args.append(f'-DCMAKE_OSX_DEPLOYMENT_TARGET={deployment_target}')
                
            build_args += ['--', '-j2']
        else:
            cmake_args += [f'-DCMAKE_BUILD_TYPE={cfg}']
            build_args += ['--', '-j2']

        if os.path.exists(self.build_temp):
            shutil.rmtree(self.build_temp)
        os.makedirs(self.build_temp)

        # Remove stale CMakeCache.txt in root if it exists
        stale_cache = os.path.join(ext.sourcedir, 'CMakeCache.txt')
        if os.path.exists(stale_cache):
            os.remove(stale_cache)

        # Always run cmake to ensure correct configuration
        print(f"Configuring with: {cmake_bin} {ext.sourcedir} {' '.join(cmake_args)}")
        subprocess.check_call([cmake_bin, ext.sourcedir] + cmake_args, cwd=self.build_temp)
        
        print(f"Building with: {cmake_bin} --build . {' '.join(build_args)}")
        subprocess.check_call([cmake_bin, '--build', '.'] + build_args, cwd=self.build_temp)

        # On Windows, editable installs might not find the .pyd if it's buried in build/
        # Copy it back to the source directory
        if platform.system() == "Windows":
            import glob
            # Look for the .pyd in the temp build dir
            for pyd in glob.glob(os.path.join(self.build_temp, "**", "*.pyd"), recursive=True):
                dest = os.path.join(extdir, os.path.basename(pyd))
                if os.path.abspath(pyd) != os.path.abspath(dest):
                    print(f"Copying {pyd} to {dest}")
                    shutil.copy(pyd, dest)

setup(
    packages=find_packages('src/python'),
    package_dir={'': 'src/python'},
    ext_modules=[CMakeExtension('rc_tui._rctui_core')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
