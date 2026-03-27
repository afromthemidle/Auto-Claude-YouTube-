package com.recipediet.app.ui

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import com.recipediet.app.data.repository.UserPreferencesRepository
import com.recipediet.app.databinding.ActivitySplashBinding
import com.recipediet.app.ui.onboarding.OnboardingActivity

@SuppressLint("CustomSplashScreen")
class SplashActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySplashBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySplashBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val userRepo = UserPreferencesRepository(this)

        Handler(Looper.getMainLooper()).postDelayed({
            val intent = if (userRepo.isOnboardingDone()) {
                Intent(this, MainActivity::class.java)
            } else {
                Intent(this, OnboardingActivity::class.java)
            }
            startActivity(intent)
            finish()
        }, 1800)
    }
}
