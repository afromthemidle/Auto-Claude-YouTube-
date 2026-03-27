package com.recipediet.app.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.recipediet.app.databinding.ItemStepBinding

class StepAdapter(private val steps: List<String>) :
    RecyclerView.Adapter<StepAdapter.ViewHolder>() {

    inner class ViewHolder(private val binding: ItemStepBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(step: String, position: Int) {
            binding.tvStepNumber.text = (position + 1).toString()
            binding.tvStep.text = step
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemStepBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(steps[position], position)
    }

    override fun getItemCount() = steps.size
}
