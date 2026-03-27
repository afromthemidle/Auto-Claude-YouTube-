package com.recipediet.app.data.model

enum class Allergy(val displayName: String, val emoji: String) {
    NUTS("Frutos Secos", "🥜"),
    GLUTEN("Gluten", "🌾"),
    DAIRY("Lácteos", "🧀"),
    EGGS("Huevos", "🥚"),
    SOY("Soya", "🫘"),
    SHELLFISH("Mariscos", "🦐"),
    FISH("Pescado", "🐟"),
    SESAME("Ajonjolí", "🌿")
}
