#include "Renderer.hpp"

Renderer::Renderer(Terminal& term) : terminal(term), last_style({-1, -1, -1, -1, -1, -1, false}) {}

void Renderer::reset() {
    last_style = {-1, -1, -1, -1, -1, -1, false};
}

void Renderer::render(const Buffer& current, const Buffer& next) {
    int width = next.getWidth();
    int height = next.getHeight();

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const Cell& curr_cell = current.getCell(x, y);
            const Cell& next_cell = next.getCell(x, y);

            if (curr_cell != next_cell) {
                terminal.setCursorPosition(x + 1, y + 1);
                
                if (next_cell.style != last_style) {
                    terminal.setForegroundColor(next_cell.style.fg_r, next_cell.style.fg_g, next_cell.style.fg_b);
                    terminal.setBackgroundColor(next_cell.style.bg_r, next_cell.style.bg_g, next_cell.style.bg_b);
                    last_style = next_cell.style;
                }
                
                std::string s;
                s += next_cell.character;
                terminal.write(s);
            }
        }
    }
    terminal.flush();
}
