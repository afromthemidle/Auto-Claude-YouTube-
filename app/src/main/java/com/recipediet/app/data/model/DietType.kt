package com.recipediet.app.data.model

enum class DietType(val displayName: String, val emoji: String, val description: String) {
    OMNIVORE("Omnívoro", "🍖", "Sin restricciones alimentarias"),
    VEGETARIAN("Vegetariano", "🥦", "Sin carne, pero incluye lácteos y huevos"),
    VEGAN("Vegano", "🌱", "Solo alimentos de origen vegetal"),
    KETO("Keto", "🥑", "Alta en grasas, muy baja en carbohidratos"),
    PALEO("Paleo", "🍗", "Alimentos naturales sin procesados"),
    GLUTEN_FREE("Sin Gluten", "🌾", "Apto para celíacos"),
    LOW_CARB("Bajo en Carbos", "🥗", "Reducción moderada de carbohidratos"),
    MEDITERRANEAN("Mediterránea", "🫒", "Rica en frutas, verduras y aceite de oliva"),
    DAIRY_FREE("Sin Lácteos", "🥛", "Sin productos lácteos"),
    HIGH_PROTEIN("Alto en Proteína", "💪", "Rica en proteínas para músculo")
}
