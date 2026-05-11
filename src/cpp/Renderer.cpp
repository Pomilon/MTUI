#include "Renderer.hpp"

Renderer::Renderer(Terminal& term) : terminal(term), last_style({-1, -1, -1, -1, -1, -1, false, false, false, false}) {}

void Renderer::reset() {
    last_style = {-1, -1, -1, -1, -1, -1, false, false, false, false};
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
                    if (next_cell.style.fg_r != last_style.fg_r || 
                        next_cell.style.fg_g != last_style.fg_g || 
                        next_cell.style.fg_b != last_style.fg_b) {
                        terminal.setForegroundColor(next_cell.style.fg_r, next_cell.style.fg_g, next_cell.style.fg_b);
                    }
                    if (next_cell.style.bg_r != last_style.bg_r || 
                        next_cell.style.bg_g != last_style.bg_g || 
                        next_cell.style.bg_b != last_style.bg_b) {
                        terminal.setBackgroundColor(next_cell.style.bg_r, next_cell.style.bg_g, next_cell.style.bg_b);
                    }
                    if (next_cell.style.bold != last_style.bold) {
                        terminal.setBold(next_cell.style.bold);
                    }
                    if (next_cell.style.italic != last_style.italic) {
                        terminal.setItalic(next_cell.style.italic);
                    }
                    if (next_cell.style.underline != last_style.underline) {
                        terminal.setUnderline(next_cell.style.underline);
                    }
                    if (next_cell.style.strikethrough != last_style.strikethrough) {
                        terminal.setStrikethrough(next_cell.style.strikethrough);
                    }
                    last_style = next_cell.style;
                }
                
                terminal.write(next_cell.character);
            }
        }
    }
    terminal.flush();
}
