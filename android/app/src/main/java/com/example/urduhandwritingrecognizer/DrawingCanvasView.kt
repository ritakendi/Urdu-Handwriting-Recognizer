package com.example.urduhandwritingrecognizer

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.view.View
import android.graphics.Paint
import android.graphics.Path
import android.view.MotionEvent

class DrawingCanvasView(context: Context) : View(context) {
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(Color.WHITE)
        for (stroke in strokes) {
            canvas.drawPath(stroke, paint)
        }
    }
    private val strokes = mutableListOf<Path>()
    private var currentStroke: Path? = null

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLACK
        style = Paint.Style.STROKE
        strokeWidth = 18f
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
    }
    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                val stroke = Path()
                stroke.moveTo(event.x, event.y)
                strokes.add(stroke)
                currentStroke = stroke
            }

            MotionEvent.ACTION_MOVE -> {
                currentStroke?.lineTo(event.x, event.y)
                invalidate()
            }

            MotionEvent.ACTION_UP -> {
                currentStroke = null
            }
        }
        return true
    }
    fun clearCanvas() {
        strokes.clear()
        currentStroke = null
        invalidate()
    }
    fun undoLastStroke() {
        if (strokes.isNotEmpty()) {
            strokes.removeAt(strokes.lastIndex)
        }
        currentStroke = null
        invalidate()
    }
}