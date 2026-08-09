#include <iostream>
#include <vector>

class PhysicsEngine {
public:
    void updatePositions() {
        std::cout << "Updating physics..." << std::endl;
    }
};

int main() {
    PhysicsEngine engine;
    engine.updatePositions();
    return 0;
}
