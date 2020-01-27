/* class Array{
private:
    Point array[40][40];
public:
    void generateArray(int x, int y) {
        Point dot(0,0);
        for(int k = 0; k <= x; k++){
            dot.setX(-200 + BORDER_WIDTH - 2 + (k * ARRAY_WIDTH));

            for(int i = 0; i <= y; i++){
                dot.setY(200 - BORDER_WIDTH - (i * ARRAY_WIDTH));
                drawDot(dot);
            }
        }
    }
} */