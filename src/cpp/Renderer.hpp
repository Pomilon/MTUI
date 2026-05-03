#ifndef RENDERER_HPP
#define RENDERER_HPP

#include "Terminal.hpp"
#include "Buffer.hpp"

class Renderer {
public:
    Renderer(Terminal& term);
    void render(const Buffer& current, const Buffer& next);
    void reset();

private:
    Terminal& terminal;
    Style last_style;
};

#endif
