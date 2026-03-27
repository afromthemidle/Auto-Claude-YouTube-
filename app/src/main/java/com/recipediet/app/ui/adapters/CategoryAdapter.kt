package com.recipediet.app.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.recipediet.app.data.model.RecipeCategory
import com.recipediet.app.databinding.ItemCategoryBinding

class CategoryAdapter(
    private val onCategoryClick: (RecipeCategory?) -> Unit
) : RecyclerView.Adapter<CategoryAdapter.ViewHolder>() {

    private var selectedCategory: RecipeCategory? = null

    private val categories = listOf(null) + RecipeCategory.values().toList()

    inner class ViewHolder(private val binding: ItemCategoryBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(category: RecipeCategory?) {
            binding.apply {
                if (category == null) {
                    chipCategory.text = "🍽️ Todos"
                } else {
                    chipCategory.text = "${category.emoji} ${category.displayName}"
                }
                chipCategory.isChecked = (category == selectedCategory)
                chipCategory.setOnClickListener {
                    selectedCategory = category
                    notifyDataSetChanged()
                    onCategoryClick(category)
                }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemCategoryBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(categories[position])
    }

    override fun getItemCount() = categories.size
}
