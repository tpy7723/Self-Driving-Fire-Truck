package com.example.root.layout;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

public class SplashActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Intent intent = new Intent(this, MainActivity.class); // 다음에 넘어갈 액티비티
        intent.putExtra("state", "launch");
        startActivity(intent);

        finish();
    }
}