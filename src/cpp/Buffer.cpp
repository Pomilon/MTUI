#include "Buffer.hpp"

Buffer::Buffer(int width, int height) : width(width), height(height) {
    cells.resize(width * height);
}

void Buffer::setCell(int x, int y, std::string c, Style s) {
    if (x >= 0 && x < width && y >= 0 && y < height) {
        cells[y * width + x] = {c, s};
    }
}

Cell Buffer::getCell(int x, int y) const {
    if (x >= 0 && x < width && y >= 0 && y < height) {
        return cells[y * width + x];
    }
    return Cell();
}

void Buffer::clear() {
    for (auto& cell : cells) {
        cell = Cell();
    }
}

void Buffer::fillRect(int x, int y, int w, int h, Style s) {
    int x1 = std::max(x, 0);
    int y1 = std::max(y, 0);
    int x2 = std::min(x + w, width);
    int y2 = std::min(y + h, height);

    for (int j = y1; j < y2; ++j) {
        for (int i = x1; i < x2; ++i) {
            cells[j * width + i] = {" ", s};
        }
    }
}

void Buffer::drawText(int x, int y, const std::string& text, Style s) {
    if (y < 0 || y >= height) return;
    
    int cur_x = x;
    for (size_t i = 0; i < text.length(); ) {
        unsigned char c = text[i];
        int len = 1;
        if (c >= 0xf0) len = 4;
        else if (c >= 0xe0) len = 3;
        else if (c >= 0xc0) len = 2;
        
        if (i + len > text.length()) break;
        
        std::string char_str = text.substr(i, len);
        setCell(cur_x, y, char_str, s);
        
        cur_x++;
        i += len;
    }
}

void Buffer::drawRect(int x, int y, int w, int h, Style s, int type) {
    if (w <= 0 || h <= 0) return;
    
    const char* chars[6]; // tl, tr, bl, br, h, v
    if (type == 1) { // Double
        chars[0] = "╔"; chars[1] = "╗"; chars[2] = "╚"; chars[3] = "╝"; chars[4] = "═"; chars[5] = "║";
    } else if (type == 2) { // Rounded
        chars[0] = "╭"; chars[1] = "╮"; chars[2] = "╰"; chars[3] = "╯"; chars[4] = "─"; chars[5] = "│";
    } else { // Single
        chars[0] = "┌"; chars[1] = "┐"; chars[2] = "└"; chars[3] = "┘"; chars[4] = "─"; chars[5] = "│";
    }

    // Horizontal borders
    for (int i = 0; i < w; ++i) {
        setCell(x + i, y, chars[4], s);
        setCell(x + i, y + h - 1, chars[4], s);
    }
    // Vertical borders
    for (int j = 0; j < h; ++j) {
        setCell(x, y + j, chars[5], s);
        setCell(x + w - 1, y + j, chars[5], s);
    }
    // Corners
    setCell(x, y, chars[0], s);
    setCell(x + w - 1, y, chars[1], s);
    setCell(x, y + h - 1, chars[2], s);
    setCell(x + w - 1, y + h - 1, chars[3], s);
}

#include <sstream>

void Buffer::drawMarkdown(int x, int y, int w, int h, const std::string& text, Style s, int cx, int cy, int cw, int ch) {
    if (y < 0 || y >= height) return;
    std::istringstream iss(text);
    std::string line;
    int curr_y = y;
    bool in_code_block = false;

    while (std::getline(iss, line) && curr_y < y + h && curr_y < height) {
        if (!line.empty() && line.back() == '\r') line.pop_back();

        if (line.length() >= 3 && line.substr(0, 3) == "```") {
            in_code_block = !in_code_block;
            curr_y++;
            continue;
        }

        Style current_style = s;

        if (in_code_block) {
            current_style.bg_r = 40; current_style.bg_g = 40; current_style.bg_b = 40;
            if (!line.empty()) {
                int render_y = curr_y;
                if (render_y >= cy && render_y < cy + ch) {
                    int curr_x = x + 2;
                    for (size_t i = 0; i < line.length(); ) {
                        unsigned char c = line[i];
                        int len = 1;
                        if (c >= 0xf0) len = 4; else if (c >= 0xe0) len = 3; else if (c >= 0xc0) len = 2;
                        if (i + len > line.length()) break;
                        if (curr_x >= cx && curr_x < cx + cw) {
                            setCell(curr_x, render_y, line.substr(i, len), current_style);
                        }
                        curr_x++; i += len;
                    }
                }
            }
            curr_y++;
            continue;
        }

        int heading_level = 0;
        size_t h_idx = 0;
        while (h_idx < line.length() && line[h_idx] == '#') {
            heading_level++;
            h_idx++;
        }
        if (heading_level > 0 && h_idx < line.length() && line[h_idx] == ' ') {
            current_style.bold = true;
            current_style.fg_r = 100; current_style.fg_g = 200; current_style.fg_b = 255;
            line = line.substr(h_idx + 1);
        } else {
            heading_level = 0;
        }

        int curr_x = x;
        int spaces = 0;
        while (spaces < line.length() && line[spaces] == ' ') spaces++;
        if (spaces + 2 <= line.length() && (line.substr(spaces, 2) == "- " || line.substr(spaces, 2) == "* ")) {
            curr_x += spaces;
            if (curr_y >= cy && curr_y < cy + ch) {
                if (curr_x >= cx && curr_x < cx + cw) setCell(curr_x, curr_y, " ", current_style);
                if (curr_x+1 >= cx && curr_x+1 < cx + cw) setCell(curr_x+1, curr_y, " ", current_style);
                if (curr_x+2 >= cx && curr_x+2 < cx + cw) setCell(curr_x+2, curr_y, "•", current_style);
                if (curr_x+3 >= cx && curr_x+3 < cx + cw) setCell(curr_x+3, curr_y, " ", current_style);
            }
            curr_x += 4;
            line = line.substr(spaces + 2);
        }

        bool is_bold = false;
        bool is_italic = false;
        bool is_code = false;

        if (curr_y >= cy && curr_y < cy + ch) {
            for (size_t i = 0; i < line.length(); ) {
                if (i + 1 < line.length() && (line.substr(i, 2) == "**" || line.substr(i, 2) == "__")) {
                    is_bold = !is_bold;
                    i += 2; continue;
                }
                if (line[i] == '*' || line[i] == '_') {
                    is_italic = !is_italic;
                    i += 1; continue;
                }
                if (line[i] == '`') {
                    is_code = !is_code;
                    i += 1; continue;
                }

                Style char_style = current_style;
                if (is_bold) char_style.bold = true;
                if (is_italic) { char_style.fg_r = 200; char_style.fg_g = 200; char_style.fg_b = 200; }
                if (is_code) { char_style.bg_r = 60; char_style.bg_g = 60; char_style.bg_b = 60; }

                unsigned char c = line[i];
                int len = 1;
                if (c >= 0xf0) len = 4; else if (c >= 0xe0) len = 3; else if (c >= 0xc0) len = 2;
                if (i + len > line.length()) break;
                
                if (curr_x >= cx && curr_x < cx + cw) {
                    setCell(curr_x, curr_y, line.substr(i, len), char_style);
                }
                curr_x++; i += len;
            }
        }
        curr_y++;
        if (heading_level > 0) curr_y++;
    }
}
