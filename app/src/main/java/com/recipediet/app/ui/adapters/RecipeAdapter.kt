package com.recipediet.app.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.recipediet.app.data.model.Recipe
import com.recipediet.app.databinding.ItemRecipeBinding

class RecipeAdapter(
    private val onRecipeClick: (Recipe) -> Unit,
    private val onFavoriteClick: (Recipe) -> Unit
) : ListAdapter<Recipe, RecipeAdapter.ViewHolder>(DiffCallback) {

    inner class ViewHolder(private val binding: ItemRecipeBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(recipe: Recipe) {
            binding.apply {
                tvEmoji.text = recipe.imageEmoji
                tvRecipeName.text = recipe.name
                tvDescription.text = recipe.description
                tvCalories.text = "${recipe.calories} kcal"
                tvTime.text = "${recipe.prepTimeMinutes + recipe.cookTimeMinutes} min"
                tvDifficulty.text = recipe.difficulty.displayName
                tvCategory.text = "${recipe.category.emoji} ${recipe.category.displayName}"
                tvRating.text = recipe.rating.toString()
                tvServings.text = "${recipe.servings} por."

                btnFavorite.setIconResource(
                    if (recipe.isFavorite) android.R.drawable.btn_star_big_on
                    else android.R.drawable.btn_star_big_off
                )

                btnFavorite.setOnClickListener { onFavoriteClick(recipe) }
                root.setOnClickListener { onRecipeClick(recipe) }

                chipDiet.text = recipe.dietTypes.firstOrNull()?.let {
                    "${it.emoji} ${it.displayName}"
                } ?: ""
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemRecipeBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    companion object {
        private val DiffCallback = object : DiffUtil.ItemCallback<Recipe>() {
            override fun areItemsTheSame(oldItem: Recipe, newItem: Recipe) = oldItem.id == newItem.id
            override fun areContentsTheSame(oldItem: Recipe, newItem: Recipe) = oldItem == newItem
        }
    }
}
