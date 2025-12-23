package com.bassma.recipebuddy.di

import com.bassma.recipebuddy.data.api.RecipeApiService
import com.bassma.recipebuddy.data.repository.RecipeRepositoryImpl
import com.bassma.recipebuddy.domain.repository.RecipeRepository
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Simple dependency injection module.
 * For production apps, consider using Hilt or Koin.
 */
object AppModule {
    
    // Backend URL - replace with your deployed backend URL or local IP for development
    // Example: "http://10.0.2.2:5000/" for Android emulator localhost
    private const val BASE_URL = "YOUR_BACKEND_URL/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val apiService: RecipeApiService = retrofit.create(RecipeApiService::class.java)
    
    val recipeRepository: RecipeRepository = RecipeRepositoryImpl(apiService)
}
