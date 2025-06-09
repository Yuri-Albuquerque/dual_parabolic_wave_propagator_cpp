#include "Parabola.h"
#include <cmath>
#include <algorithm>

namespace WaveSimulation {

Parabola::Parabola(double diameter, double focus, const Point2D& vertex, bool concaveUp)
    : m_diameter(diameter), m_focus(focus), m_vertex(vertex), m_concaveUp(concaveUp) {
    m_coefficient = calculateCoefficient();
}

double Parabola::calculateCoefficient() const {
    // For parabola: y = a(x - h)^2 + k where (h,k) is vertex
    // Standard form: y - k = a(x - h)^2
    // For focus at distance f from vertex: a = ±1/(4f)
    double a = 1.0 / (4.0 * m_focus);
    return m_concaveUp ? a : -a;
}

double Parabola::getY(double x) const {
    // y = a(x - h)^2 + k
    double dx = x - m_vertex.x;
    return m_coefficient * dx * dx + m_vertex.y;
}

bool Parabola::containsPoint(const Point2D& point) const {
    // Check if point is within diameter bounds
    if (std::abs(point.x - m_vertex.x) > m_diameter / 2.0) {
        return false;
    }
    
    double parabolaY = getY(point.x);
    
    if (m_concaveUp) {
        // For concave up parabola, point should be above the curve
        return point.y >= parabolaY;
    } else {
        // For concave down parabola, point should be below the curve
        return point.y <= parabolaY;
    }
}

ParabolaParams Parabola::getParams() const {
    ParabolaParams params;
    params.diameter = m_diameter;
    params.focus = m_focus;
    params.vertex = m_vertex;
    params.coefficient = m_coefficient;
    params.concaveUp = m_concaveUp;
    return params;
}

Point2D Parabola::getNormal(double x) const {
    // For parabola y = ax^2 + bx + c, dy/dx = 2ax + b
    // For our form y = a(x-h)^2 + k, dy/dx = 2a(x-h)
    double dx = x - m_vertex.x;
    double slope = 2.0 * m_coefficient * dx;
    
    // Normal vector is perpendicular to tangent
    // If tangent slope is m, normal slope is -1/m
    // Normal vector: (1, -1/m) normalized
    double normalSlope = -1.0 / slope;
    
    // Normalize the normal vector
    double length = std::sqrt(1.0 + normalSlope * normalSlope);
    
    return Point2D(1.0 / length, normalSlope / length);
}

Point2D Parabola::getReflectionDirection(const Point2D& point, const Point2D& incoming) const {
    Point2D normal = getNormal(point.x);
    
    // Reflection formula: R = I - 2(I·N)N
    // where I is incoming direction, N is normal, R is reflected direction
    double dotProduct = incoming.x * normal.x + incoming.y * normal.y;
    
    Point2D reflected;
    reflected.x = incoming.x - 2.0 * dotProduct * normal.x;
    reflected.y = incoming.y - 2.0 * dotProduct * normal.y;
    
    return reflected;
}

} // namespace WaveSimulation
