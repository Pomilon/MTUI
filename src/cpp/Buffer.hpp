#ifndef BUFFER_HPP
#define BUFFER_HPP

#include <vector>
#include <string>

struct Style {
    int fg_r, fg_g, fg_b;
    int bg_r, bg_g, bg_b;
    bool bold = false;

    bool operator==(const Style& other) const {
        return fg_r == other.fg_r && fg_g == other.fg_g && fg_b == other.fg_b &&
               bg_r == other.bg_r && bg_g == other.bg_g && bg_b == other.bg_b &&
               bold == other.bold;
    }
    bool operator!=(const Style& other) const { return !(*this == other); }
};

struct Cell {
    std::string character = " ";
    Style style = {255, 255, 255, 0, 0, 0, false};

    bool operator==(const Cell& other) const {
        return character == other.character && style == other.style;
    }
    bool operator!=(const Cell& other) const { return !(*this == other); }
};

class Buffer {
public:
    Buffer(int width, int height);
    
    void setCell(int x, int y, std::string c, Style s);
    Cell getCell(int x, int y) const;
    
    int getWidth() const { return width; }
    int getHeight() const { return height; }
    
    void clear();

    void fillRect(int x, int y, int w, int h, Style s);
    void drawText(int x, int y, const std::string& text, Style s);
    void drawRect(int x, int y, int w, int h, Style s, int type = 0);
    void drawMarkdown(int x, int y, int w, int h, const std::string& text, Style s, int cx, int cy, int cw, int ch);

    const std::vector<Cell>& getCells() const { return cells; }

private:
    int width, height;
    std::vector<Cell> cells;
};

#endif
