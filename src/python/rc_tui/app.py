from .core import Element, Component
from .reconciler import build_tree
from .layout import measure, do_layout
from .render import draw_tree, draw_inspector
from .input import InputManager, MouseEvent, KeyEvent
from .canvas import Canvas
from .dom import SelectMenu, Box, ScrollBox, Button
from . import tui_core
import time
import traceback
import sys

class App:
    def __init__(self, root_comp_cls, props=None, debug_file=None, terminal=None):
        self.terminal = terminal or tui_core.Terminal()
        
        # Only enable raw mode and tracking if it's a real terminal we can control
        if hasattr(self.terminal, 'enable_raw_mode'):
            self.terminal.enable_raw_mode()
        if hasattr(self.terminal, 'enter_alternate_screen'):
            self.terminal.enter_alternate_screen()
        if hasattr(self.terminal, 'enable_mouse_tracking'):
            self.terminal.enable_mouse_tracking()
        
        # Only write to stdout if it's not a mock (or if it's a mock that handles it)
        if not terminal:
            sys.stdout.write("\x1b[?1003h\x1b[?1006h")
            sys.stdout.flush()
        
        # Debug logging
        self.debug_file = debug_file
        if self.debug_file:
            with open(self.debug_file, "w") as f:
                f.write(f"--- RC-TUI Log Start: {time.ctime()} ---\n")

        cols, rows = self.terminal.get_size()
        self.log(f"Terminal size: {cols}x{rows}")
        self.curr_buffer = tui_core.Buffer(cols, rows)
        self.next_buffer = tui_core.Buffer(cols, rows)

        # Only create renderer if terminal is the expected C++ type
        if isinstance(self.terminal, tui_core.Terminal):
            self.renderer = tui_core.Renderer(self.terminal)
        else:
            self.renderer = None
            
        self.canvas = Canvas(self.next_buffer)
        self.canvas.app = self

        # We now manage a stack of windows. Each window is (element, node)
        self.windows = []
        main_props = props or {}
        main_props['app'] = self
        self.windows.append({'element': Element(root_comp_cls, main_props), 'node': None})
        
        self.input_manager = InputManager()
        self.needs_render = True
        self._running = False
        self.notifications = [] 
        self.show_inspector = False # Global inspector flag
        self.mouse_x = -1
        self.mouse_y = -1
        self.hovered_node = None
        self.focused_node = None
        self._pending_effects = []

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        # Run cleanups for all windows
        try:
            from .reconciler import _unmount_node
            for win in self.windows:
                if win.get('node'):
                    _unmount_node(win['node'])
        except (ImportError, AttributeError, NameError):
            pass

        if hasattr(self, 'terminal'):
            try:
                if not isinstance(self.terminal, tui_core.Terminal):
                    return
                sys.stdout.write("\x1b[?1003l") # Disable motion tracking
                sys.stdout.flush()
                self.terminal.disable_mouse_tracking()
                self.terminal.exit_alternate_screen()
                self.terminal.disable_raw_mode()
            except (AttributeError, TypeError, NameError):
                pass

    def log(self, message):
        if self.debug_file:
            with open(self.debug_file, "a") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] {message}\n")

    def log_error(self, err_msg):
        self.log(f"ERROR: {err_msg}")
        self.log(traceback.format_exc())

    def notify(self, text, duration=3.0):
        # Prevent duplicate notifications spamming the screen
        if self.notifications and self.notifications[-1]['text'] == text:
            self.notifications[-1]['time'] = time.time()
            return

        self.notifications.append({
            "text": text,
            "time": time.time(),
            "duration": duration
        })
        self.request_render()

    def open_window(self, element):
        element.props['app'] = self
        self.windows.append({'element': element, 'node': None})
        self.request_render()

    def close_window(self):
        if len(self.windows) > 1:
            win = self.windows.pop()
            if win.get('node'):
                from .reconciler import _unmount_node
                _unmount_node(win['node'])
            self.request_render()

    def request_render(self):
        self.needs_render = True

    def _step(self):
        try:
            # Check for resize
            cols, rows = self.terminal.get_size()
            resized = False
            if cols != self.canvas.width or rows != self.canvas.height:
                self.terminal.clear_screen()
                if self.renderer:
                    self.renderer.reset()
                self.curr_buffer = tui_core.Buffer(cols, rows)
                self.next_buffer = tui_core.Buffer(cols, rows)
                self.canvas = Canvas(self.next_buffer)
                self.canvas.app = self
                resized = True

            self.next_buffer.clear()
            self.canvas.buffer = self.next_buffer
            # Reset canvas state for this frame
            self.canvas._clip_stack = [(0, 0, self.canvas.width, self.canvas.height)]
            
            # Reconcile and layout windows
            for i, win in enumerate(self.windows):
                if self.needs_render or resized or win['node'] is None:
                    win['node'] = build_tree(win['element'], self, win['node'])
                    measure(win['node'], self.canvas.width, self.canvas.height)
                    do_layout(win['node'], 0, 0, self.canvas.width, self.canvas.height)
            
            # Draw windows from bottom to top
            for i, win in enumerate(self.windows):
                if i > 0 and win['element'].props.get('dim', True):
                    dim_style = tui_core.Style(15, 15, 15, 5, 5, 5, False)
                    # Use fill_rect which is clipped
                    self.canvas.fill_rect(0, 0, self.canvas.width, self.canvas.height, dim_style)
                
                if win['node']:
                    draw_tree(win['node'], self.canvas)

            # Global Inspector Pass (ignores previous clip stacks)
            if self.show_inspector and self.hovered_node:
                self.canvas._clip_stack = [(0, 0, self.canvas.width, self.canvas.height)]
                draw_inspector(self.hovered_node, self.canvas)

            # Draw Notifications
            self._render_notifications()
            
            # Draw Tooltips
            self._render_tooltip()
            
            if self.renderer:
                self.renderer.render(self.curr_buffer, self.next_buffer)
                self.curr_buffer, self.next_buffer = self.next_buffer, self.curr_buffer
            
            self.needs_render = False
            # Run pending effects after paint
            effects = self._pending_effects
            self._pending_effects = []
            for instance, idx in effects:
                instance.run_effect(idx)
        except Exception as e:
            self.log_error(f"Render Step Failure: {e}")
        finally:
            self.needs_render = False

    def _render_notifications(self):
        now = time.time()
        self.notifications = [n for n in self.notifications if now - n['time'] < n['duration']]
        
        if not self.notifications:
            return

        margin = 1
        curr_y = self.canvas.height - margin
        
        for n in reversed(self.notifications):
            text = n['text']
            w = len(text) + 4
            h = 3
            x = self.canvas.width - w - margin
            y = curr_y - h
            
            style = tui_core.Style(255, 255, 255, 30, 30, 50, False)
            self.canvas.fill_rect(x, y, w, h, style)
            self.canvas.draw_rect(x, y, w, h, style, 2)
            self.canvas.draw_text(x + 2, y + 1, text, style)
            curr_y = y - margin

    def _render_tooltip(self):
        curr = self.hovered_node
        tooltip = None
        while curr:
            tooltip = curr.props.get('tooltip')
            if tooltip:
                break
            curr = curr.parent
            
        if not tooltip:
            return
            
        text = str(tooltip)
        w = len(text) + 2
        h = 1
        x = self.mouse_x + 1
        y = self.mouse_y + 1
        
        # Keep on screen
        if x + w > self.canvas.width: x = self.mouse_x - w - 1
        if y + h > self.canvas.height: y = self.mouse_y - h - 1
        if x < 0: x = 0
        if y < 0: y = 0
        
        style = tui_core.Style(0, 0, 0, 240, 240, 150, False)
        self.canvas.fill_rect(x, y, w, h, style)
        self.canvas.draw_text(x + 1, y, text, style)

    def stop(self):
        self._running = False

    def run(self):
        self._running = True
        self.request_render()
        
        try:
            while self._running:
                # Check for resize
                cols, rows = self.terminal.get_size()
                if cols != self.canvas.width or rows != self.canvas.height:
                    self.request_render()

                if self.needs_render:
                    self._step()
                
                # Check for input
                events = self.input_manager.get_events()
                for event in events:
                    if isinstance(event, KeyEvent) and event.key == 'CTRL_C':
                        self._running = False
                        break
                    if isinstance(event, KeyEvent) and event.key == 'F12':
                        self.show_inspector = not self.show_inspector
                        self.request_render()
                        continue
                    
                    self.dispatch_event(event)
                
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def dispatch_event(self, event):
        # We dispatch to the top-most window only
        if not self.windows: return
        win = self.windows[-1]
        node = win['node']
        if not node: return
        
        if isinstance(event, MouseEvent):
            self.mouse_x = event.x
            self.mouse_y = event.y
            target = self._hit_test(node, event.x, event.y)
            
            if event.type == 'MOVE':
                if target != self.hovered_node:
                    self.hovered_node = target
                    self.request_render()
                return # We don't need to do focus/click logic for MOVE
            
            self.hovered_node = target
            
            if event.type == 'CLICK':
                focusable_types = ('input', 'button', 'checkbox', 'radiobutton', 'switch', 'select', 'tabselect', 'textarea')
                new_focus = target if target and target.type in focusable_types else None
                self._update_focus(node, new_focus)
                self.request_render()

                if target:
                    if target.type == 'tabselect':
                        options = target.props.get('options', [])
                        relative_x = event.x - target.screen_x
                        curr_x = 0
                        clicked_idx = -1
                        for i, opt in enumerate(options):
                            tab_w = len(str(opt)) + 3
                            if curr_x <= relative_x < curr_x + tab_w:
                                clicked_idx = i
                                break
                            curr_x += tab_w
                        
                        if clicked_idx != -1:
                            on_change = target.props.get('on_change')
                            if on_change:
                                on_change(clicked_idx)
                                self.request_render()

                    if target.type == 'select':
                        self._open_select_menu(target)
                        self.request_render()

                    if target.type == 'checkbox':
                        on_change = target.props.get('on_change')
                        if on_change: 
                            on_change(not target.props.get('checked', False))
                            self.request_render()
                    
                    if target.type == 'radiobutton':
                        on_change = target.props.get('on_change')
                        if on_change: 
                            on_change(True)
                            self.request_render()
                    
                    if target.type == 'switch':
                        on_change = target.props.get('on_change')
                        if on_change: 
                            on_change(not target.props.get('on', False))
                            self.request_render()

                    n = target
                    while n:
                        on_click = n.props.get('on_click')
                        if on_click:
                            try:
                                # Inspect the handler to see if it wants the event
                                if hasattr(on_click, '__code__'):
                                    num_args = on_click.__code__.co_argcount
                                    num_defaults = len(on_click.__defaults__ or [])
                                    # If it REQUIRES an argument, pass the event.
                                    # If it has 0 required args (even if it has defaults), call with none.
                                    if num_args - num_defaults > 0:
                                        on_click(event)
                                    else:
                                        on_click()
                                else:
                                    # Fallback for non-function callables
                                    try:
                                        on_click(event)
                                    except TypeError:
                                        on_click()
                            except Exception as e:
                                self.log_error(f"on_click handler error: {e}")
                                
                            self.request_render()
                            break
                        n = n.parent
                    
            elif event.type == 'SCROLL' and target:
                sb = target
                while sb and sb.type != 'scrollbox':
                    sb = sb.parent
                if sb:
                    sb.scroll_y += event.delta
                    max_scroll = max(0, sb.content_h - (sb.h - 2 if sb.props.get('border') else sb.h))
                    if sb.scroll_y < 0: sb.scroll_y = 0
                    if sb.scroll_y > max_scroll: sb.scroll_y = max_scroll
                    
                    # If the ScrollBox has an on_scroll callback (used by VirtualList), call it
                    on_scroll = sb.props.get('on_scroll')
                    if on_scroll:
                        # Pass current scroll position and the actual viewport height
                        on_scroll(sb.scroll_y, sb.h)
                        
                    self.request_render()
                        
        elif isinstance(event, KeyEvent):
            focused_node = self.focused_node
            
            if focused_node:
                # Generic key down handler
                on_key_down = focused_node.props.get('on_key_down')
                if on_key_down:
                    if on_key_down(event):
                        self.request_render()
                        return

                if focused_node.type == 'tabselect' and event.key in ('LEFT', 'RIGHT', ' ', 'ENTER'):
                    on_change = focused_node.props.get('on_change')
                    if on_change:
                        opts = focused_node.props.get('options', [])
                        idx = focused_node.props.get('selected_index', 0)
                        if event.key in ('RIGHT', ' ', 'ENTER'):
                            on_change((idx + 1) % len(opts) if opts else 0)
                        elif event.key == 'LEFT':
                            on_change((idx - 1) % len(opts) if opts else 0)
                        self.request_render()
                    return

                if focused_node.type == 'select' and event.key in (' ', 'ENTER', 'DOWN', 'UP'):
                    self._open_select_menu(focused_node)
                    self.request_render()
                    return

                if focused_node.type in ('checkbox', 'radiobutton', 'switch') and event.key in (' ', 'ENTER'):
                    on_change = focused_node.props.get('on_change')
                    if on_change: 
                        if focused_node.type == 'checkbox':
                            on_change(not focused_node.props.get('checked', False))
                        elif focused_node.type == 'radiobutton':
                            on_change(True)
                        elif focused_node.type == 'switch':
                            on_change(not focused_node.props.get('on', False))
                        self.request_render()
                    return

                if focused_node.type == 'input':
                    val = focused_node.props.get('value', '')
                    if event.key == 'BACKSPACE':
                        if val:
                            val = val[:-1]
                    elif event.key == 'ENTER':
                        on_submit = focused_node.props.get('on_submit')
                        if on_submit:
                            on_submit(val)
                            self.request_render()
                    elif len(event.key) == 1:
                        val += event.key
                    
                    if val != focused_node.props.get('value'):
                        focused_node.props['value'] = val
                        on_change = focused_node.props.get('on_change')
                        if on_change: on_change(val)
                        self.request_render()
                
                if focused_node.type == 'textarea':
                    val = focused_node.props.get('value', '')
                    if event.key == 'BACKSPACE':
                        if val: val = val[:-1]
                    elif event.key == 'ENTER':
                        val += '\n'
                    elif len(event.key) == 1:
                        val += event.key
                    
                    if val != focused_node.props.get('value'):
                        focused_node.props['value'] = val
                        on_change = focused_node.props.get('on_change')
                        if on_change: on_change(val)
                        self.request_render()

                if focused_node.type == 'button' and event.key in (' ', 'ENTER'):
                    on_click = focused_node.props.get('on_click')
                    if on_click:
                        try:
                            on_click(event)
                        except TypeError:
                            try:
                                on_click()
                            except Exception as e:
                                self.log_error(f"on_click handler error: {e}")
                        except Exception as e:
                            self.log_error(f"on_click handler error: {e}")
                    self.request_render()
                    return

            if event.key == 'TAB':
                self._cycle_focus(node)
                self.request_render()

    def _update_focus(self, node, new_focus):
        self._clear_focus(node)
        if new_focus:
            new_focus.is_focused = True
            self.focused_node = new_focus
        else:
            self.focused_node = None

    def _clear_focus(self, node):
        node.is_focused = False
        for child in node.children:
            self._clear_focus(child)

    def _cycle_focus(self, node):
        focusable_types = ('input', 'button', 'checkbox', 'radiobutton', 'switch', 'select', 'tabselect', 'textarea')
        
        all_focusable = []
        def collect(n):
            if n.type in focusable_types:
                all_focusable.append(n)
            for child in n.children:
                collect(child)
        collect(node)
        
        if not all_focusable: return
        
        current_idx = -1
        for i, n in enumerate(all_focusable):
            if n.is_focused:
                current_idx = i
                break
        
        self._clear_focus(node)
        next_idx = (current_idx + 1) % len(all_focusable)
        all_focusable[next_idx].is_focused = True
        self.focused_node = all_focusable[next_idx]

    def _hit_test(self, node, x, y):
        # 1. Check if the point is within the node's own screen bounds
        if not (node.screen_x <= x < node.screen_x + node.w and \
                node.screen_y <= y < node.screen_y + node.h):
            return None
            
        # 2. Check for clipping by parent (e.g. ScrollBox)
        # We walk up the tree and ensure the point is within the 'inner' bounds of all parents
        p = node.parent
        while p:
            inner_x = p.screen_x
            inner_y = p.screen_y
            inner_w = p.w
            inner_h = p.h
            
            if p.props.get('border'):
                inner_x += 1
                inner_y += 1
                inner_w -= 2
                inner_h -= 2
                
            if not (inner_x <= x < inner_x + inner_w and \
                    inner_y <= y < inner_y + inner_h):
                return None
            p = p.parent

        # 3. Descend into children (reverse order for top-most hit)
        for child in reversed(node.children):
            res = self._hit_test(child, x, y)
            if res: return res
            
        return node

    def _open_select_menu(self, target):
        options = target.props.get('options', [])
        on_change = target.props.get('on_change')
        
        def on_select(idx):
            if on_change: on_change(idx)
            self.close_window()
            
        menu_element = Element(SelectMenu, {
            'options': options,
            'on_select': on_select,
            'x': target.screen_x,
            'y': target.screen_y + 1,
            'width': target.w
        })
        self.open_window(menu_element)
