package com.recipediet.app.data.model

import androidx.room.TypeConverter

class ListConverters {

    @TypeConverter
    fun fromStringList(value: List<String>): String = value.joinToString("||")

    @TypeConverter
    fun toStringList(value: String): List<String> =
        if (value.isEmpty()) emptyList() else value.split("||")

    @TypeConverter
    fun fromDietTypeList(value: List<DietType>): String =
        value.joinToString(",") { it.name }

    @TypeConverter
    fun toDietTypeList(value: String): List<DietType> =
        if (value.isEmpty()) emptyList()
        else value.split(",").mapNotNull { runCatching { DietType.valueOf(it) }.getOrNull() }

    @TypeConverter
    fun fromDifficulty(value: Difficulty): String = value.name

    @TypeConverter
    fun toDifficulty(value: String): Difficulty = Difficulty.valueOf(value)

    @TypeConverter
    fun fromRecipeCategory(value: RecipeCategory): String = value.name

    @TypeConverter
    fun toRecipeCategory(value: String): RecipeCategory = RecipeCategory.valueOf(value)
}
