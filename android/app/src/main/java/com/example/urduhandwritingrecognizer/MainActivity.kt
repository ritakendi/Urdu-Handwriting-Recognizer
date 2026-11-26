package com.example.urduhandwritingrecognizer

import android.os.Bundle
import android.view.Gravity
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val welcomeMessage = TextView(this).apply {
            text = "Urdu Handwriting Recognizer\n\nThe app is ready for its first feature."
            textSize = 22f
            gravity = Gravity.CENTER
        }

        setContentView(DrawingCanvasView(this))
    }
}
