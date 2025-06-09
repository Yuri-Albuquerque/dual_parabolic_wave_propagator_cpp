#pragma once

#include "Types.h"
#include <vector>

namespace WaveSimulation {

class Parabola {
public:
    Parabola(double diameter, double focus, const Point2D& vertex, bool concaveUp);
    
    double getY(double x) const;
    bool containsPoint(const Point2D& point) const;
    ParabolaParams getParams() const;
    
    // Reflection calculation
    Point2D getReflectionDirection(const Point2D& point, const Point2D& incoming) const;
    
private:
    double calculateCoefficient() const;
    Point2D getNormal(double x) const;
    
    double m_diameter;
    double m_focus;
    Point2D m_vertex;
    bool m_concaveUp;
    double m_coefficient;
};

} // namespace WaveSimulation
