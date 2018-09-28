package com.example.root.layout;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.view.WindowManager;
import android.widget.EditText;
import android.widget.Toast;

import static com.example.root.layout.MainActivity.soundId2;

public class FirstLayout extends AppCompatActivity { // 전화번호 등록 화면

    public static String memoData = "initial"; // 어플 종료 후에도 memoData 를 불러오기 위함

    EditText mMemoEdit = null;
    TextFileManager mTextFileManager = new TextFileManager(this);

    @Override
    protected void onCreate(Bundle bundle) {
        super.onCreate(bundle);

        getWindow().setFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setContentView(R.layout.first_layout);

        mMemoEdit = (EditText) findViewById(R.id.memo_edit); // 메모 입력창
    }

    public void onClick(View v) {
        switch (v.getId()) {

            // 1. 파일에 저장된 메모 텍스트 파일 불러오기
            case R.id.load_btn: { // 불러오기 버튼
                MainActivity.sound2.play(soundId2,1f,1f,0,0,1f); // 버튼 클릭소리
                memoData = mTextFileManager.load();
                mMemoEdit.setText(memoData);

                Toast.makeText(this, "불러오기 완료", Toast.LENGTH_SHORT).show();
                break;
            }

            // 2. 에디트텍스트에 입력된 메모를 텍스트 파일로 저장하기
            case R.id.save_btn: { // 저장 버튼
                MainActivity.sound2.play(soundId2,1f,1f,0,0,1f); // 버튼 클릭소리
                memoData = mMemoEdit.getText().toString();
                mTextFileManager.save(memoData);
                mMemoEdit.setText("");

                Toast.makeText(this, "저장 완료", Toast.LENGTH_SHORT).show();
                break;
            }

            // 3. 저장된 메모 파일 삭제하기
            case R.id.delete_btn: { // 삭제 버튼
                MainActivity.sound2.play(soundId2,1f,1f,0,0,1f); // 버튼 클릭소리
                mTextFileManager.delete();
                mMemoEdit.setText("");

                Toast.makeText(this, "삭제 완료", Toast.LENGTH_SHORT).show();
            }
        }
    }
}

