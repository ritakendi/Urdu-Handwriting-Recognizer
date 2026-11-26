package com.example.urduhandwritingrecognizer

import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.view.ViewGroup
import android.view.Gravity
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val drawingCanvas = DrawingCanvasView(this)

        val clearButton = Button(this).apply {
            text = "Clear"
            setOnClickListener {
                drawingCanvas.clearCanvas()
            }
        }

        val screen = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(clearButton)
            addView(
                drawingCanvas,
                LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    0,
                    1f
                )
            )
        }
        setContentView(screen)
    }
}
