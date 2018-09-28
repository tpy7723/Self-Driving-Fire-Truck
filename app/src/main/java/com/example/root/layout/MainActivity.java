package com.example.root.layout;

import android.Manifest;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Address;
import android.location.Geocoder;
import android.media.AudioManager;
import android.media.SoundPool;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v4.widget.SwipeRefreshLayout;
import android.telephony.SmsManager;
import android.util.Log;
import android.view.View;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.view.animation.Animation;
import android.view.animation.TranslateAnimation;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.Timer;
import java.util.TimerTask;
import android.telephony.TelephonyManager;

public class MainActivity extends AppCompatActivity // 메인 화면
        implements NavigationView.OnNavigationItemSelectedListener, SwipeRefreshLayout.OnRefreshListener {

    TextView explain, phonegps, httpfire, address;
    ImageView img;
    TextFileManager mTextFileManager = new TextFileManager(this);
    SwipeRefreshLayout sr2; // swipe refresh
    static SoundPool sound; // siren sound
    static SoundPool sound2; // button sound

    private final int PERMISSIONS_ACCESS_FINE_LOCATION = 1000;
    private final int PERMISSIONS_ACCESS_COARSE_LOCATION = 1001;
    private boolean isAccessFineLocation = false;
    private boolean isAccessCoarseLocation = false;
    private boolean isPermission = false;
    public static double lati, longi,fire;
    public static String location;
    public int count;
    public int tasktime = 0;
    public String url = "http://45.77.10.162:5000/fire"; // fire URL 설정.
    public String url2 = "http://45.77.10.162:5000/gps"; // gps URL 설정.
    public static double latitu, longitu;
    static int soundId;
    static int soundId2;
    int soundcount = 0; // 반복재생 방지

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        sound = new SoundPool(5, AudioManager.STREAM_MUSIC,0);
        soundId = sound.load(this, R.raw.policesiren,1); // siren sound

        sound2 = new SoundPool(5, AudioManager.STREAM_MUSIC,0);
        soundId2 = sound2.load(this, R.raw.button,1); // button sound

        // 위젯에 대한 참조.
        explain = (TextView) findViewById(R.id.explain); // <현재 Thinkar 위치 >
        phonegps = (TextView) findViewById(R.id.phonegps); // 위도:  경도:
        address = (TextView) findViewById(R.id.address); // 주소 표시
        httpfire = (TextView) findViewById(R.id.httpfire); // 화재 유무
        img = (ImageView) findViewById(R.id.imageView4); // firetruck image

        sr2 = (SwipeRefreshLayout) findViewById(R.id.sr2);
        sr2.setOnRefreshListener(this);

        // 폰 상태 접근 권한 묻기
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE) != PackageManager.PERMISSION_GRANTED)
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_PHONE_STATE}, 50);
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS) != PackageManager.PERMISSION_GRANTED)
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.SEND_SMS}, 50);

        final TimerTask task = new TimerTask() {
            @Override
            public void run() {
                new NetworkTask(url, url2, null).execute();
                try {
                    JSONObject result = new NetworkTask(url, url2, null).execute().get();  // JSON 형식의 result

                    if (result == null) {
                        lati = 0;
                        longi = 0;
                    }

                    if (soundcount==0){ // 한번만 재생
                        sound.play(soundId,1f,1f,0,0,1f);
                        soundcount = 1;
                    }

                    String a = result.get("lati").toString(); // result 에서 latitude 항목 값을 가져옴
                    String b = result.get("longi").toString(); // result 에서 longitude 항목 값을 가져옴
                    String c = result.get("fire").toString(); // result 에서 fire 항목 값을 가져옴
                    lati = Double.parseDouble(a);  // String to Double
                    longi = Double.parseDouble(b); // String to Double
                    fire = Double.parseDouble(c); // String to Double

                    tasktime += 1;
                    if (tasktime == 500) {  // 화재 문자 중복 발송 방지
                        tasktime = 0;
                        count = 0;
                    }

                    if (fire == 1 && count == 0) { // 화재가 났을 시 문자 발송

                        count += 1;
                        if (FirstLayout.memoData.equals("initial")) { // 어플 재시작 했을 때
                            FirstLayout.memoData = mTextFileManager.load(); // 기존 메모 내용을 가져옴
                        }

                        String[] token = FirstLayout.memoData.split("\n"); // 엔터를 기준으로 split 후 배열에 저장
                        location = getAddress(MainActivity.this, lati, longi); // 위도,경도로 주소 얻기

                        try {
                            SmsManager smsManager = SmsManager.getDefault();


                            for (int i = 0; i < token.length; i++) { // 전화번호 등록개수만큼 반복

                                if (location.equals("현재 위치를 확인 할 수 없습니다.")) {
                                    Toast.makeText(getApplicationContext(), "              현재 위치를 확인 할 수 없습니다!", Toast.LENGTH_SHORT).show();
                                    break;
                                } else { // 메세지 전송
                                    long now = System.currentTimeMillis();
                                    Date date = new Date(now);
                                    SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH시 mm분 ss초");
                                    String getTime = sdf.format(date); // 현재 날짜 및 시간 정보

                                    smsManager.sendTextMessage(token[i], null, getTime + "\n" + location + "\n에서 화재가 났습니다.", null, null);
                                    Toast.makeText(getApplicationContext(), "재난 메세지 전송 완료!", Toast.LENGTH_SHORT).show();
                                }
                            }

                        } catch (Exception e) {
                            Toast.makeText(getApplicationContext(), "번호를 확인하세요!", Toast.LENGTH_SHORT).show();
                            e.printStackTrace();
                        }
                    }
                } catch (Exception e) {
                    Log.i("logerror", "timer error: "+e.toString());
                }
            }
        };
        new Timer().scheduleAtFixedRate(task, 0, 1000);  // 1초마다 asyncTask 백그라운드에서 반복

        TranslateAnimation ani = new TranslateAnimation(
                Animation.RELATIVE_TO_SELF, -1.0f,
                Animation.RELATIVE_TO_SELF, 0.1f,
                Animation.RELATIVE_TO_SELF, 0.0f,
                Animation.RELATIVE_TO_SELF, 0.0f);
        ani.setFillAfter(true); // 애니메이션 후 이동한좌표에 stop
        ani.setDuration(2500); //지속시간

        img.startAnimation(ani); // image move

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab); // 문자 message 아이콘
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (FirstLayout.memoData.equals("initial")) { // 어플 재시작 했을 때
                    FirstLayout.memoData = mTextFileManager.load(); // 기존 메모 내용을 가져옴
                }

                sound2.play(soundId2,1f,1f,0,0,1f); // button sound

                String[] token = FirstLayout.memoData.split("\n"); // 엔터를 기준으로 split 후 배열에 저장
                location = getAddress(MainActivity.this, lati, longi); // 위도,경도로 주소 얻기

                try {
                    SmsManager smsManager = SmsManager.getDefault();

                    for (int i = 0; i < token.length; i++) { // 전화번호 등록개수만큼 반복

                        long now = System.currentTimeMillis();
                        Date date = new Date(now);
                        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH시 mm분 ss초");
                        String getTime = sdf.format(date); // 현재 날짜 및 시간 정보

                        if (location.equals("현재 위치를 확인 할 수 없습니다.")) {
                            Snackbar.make(view, "              현재 위치를 확인 할 수 없습니다!", Snackbar.LENGTH_LONG)
                                    .setAction("Action", null).show();
                            break;
                        } else { // 메세지 전송
                            smsManager.sendTextMessage(token[i], null, getTime + "\n" + location + "\n에서 화재가 났습니다.", null, null);
                            Snackbar.make(view, "                    재난 메세지 전송 완료!", Snackbar.LENGTH_LONG)
                                    .setAction("Action", null).show();
                        }
                    }
                } catch (Exception e) {
                    Snackbar.make(view, "                      번호를 확인하세요!", Snackbar.LENGTH_LONG)
                            .setAction("Action", null).show();
                    e.printStackTrace();
                }
            }
        });

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout); // menu bar
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view); // menu bar 상단 이미지
        navigationView.setNavigationItemSelectedListener(this);
    }

    @Override
    public void onBackPressed() { // menu bar
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) { // menu bar
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) { // menu bar
        int id = item.getItemId();
        sound2.play(soundId2,1f,1f,0,0,1f);

        if (id == R.id.action_settings) { // 스마트폰 설정창 이동
            Intent intent = new Intent();
            intent.setClassName("com.android.settings", "com.android.settings.Settings");
            startActivity(intent);
        }

        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) { // menu bar
        int id = item.getItemId();
        sound2.play(soundId2,1f,1f,0,0,1f);

        if (id == R.id.nav_first_layout) { // 전화번호 등록 버튼 클릭 시 FirstLayout
            Intent intent = new Intent(getApplicationContext(), FirstLayout.class);
            startActivity(intent);
        } else if (id == R.id.nav_second_layout) { // 실시간 영상 버튼 클릭 시 SecondLayout
            Intent intent = new Intent(getApplicationContext(), SecondLayout.class);
            startActivity(intent);
        }
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    @Override
    public void onRefresh() { // swipe refresh
        ImageView img = (ImageView) findViewById(R.id.imageView4);

        sound.play(soundId,1f,1f,0,0,1f);

        TranslateAnimation ani = new TranslateAnimation(
                Animation.RELATIVE_TO_SELF, -1.0f,
                Animation.RELATIVE_TO_SELF, 0.1f,
                Animation.RELATIVE_TO_SELF, 0.0f,
                Animation.RELATIVE_TO_SELF, 0.0f);
        ani.setFillAfter(true); // 애니메이션 후 이동한좌표에 stop
        ani.setDuration(2500); //지속시간

        img.startAnimation(ani); // image move
        sr2.setRefreshing(false); // remove 화살표
    }

    public class NetworkTask extends AsyncTask<Void, Void, JSONObject> {
        private String url; // fire
        private String url2; // gps
        private ContentValues values;

        public NetworkTask(String url, String url2, ContentValues values) {
            this.url = url; // fire
            this.url2 = url2; // gps
            this.values = values; // null
        }  // 생성자

        @Override
        protected JSONObject doInBackground(Void... params) { // 백그라운드에서 실행
            JSONObject result; // json 형식 ( 정보를 받아옴 )
            JSONParser parser = new JSONParser(); // json parsing

            RequestHttpURLConnection requestHttpURLConnection = new RequestHttpURLConnection();

            try {
                // 기기 고유번호 얻기
                String myDeviceId = getDeviceId(); // my phone ID

                if (myDeviceId.equals("358705081221691")) { // my phone ID
                    double currentlongi = SecondLayout.currentlongi;
                    double currentlati = SecondLayout.currentlati;

                    RequestHttpURLConnection requestHttpURLConnection2 = new RequestHttpURLConnection();
                    requestHttpURLConnection2.request("http://45.77.10.162:5000/gps/insert?lati=" + String.valueOf(currentlati) + "&" + "longi=" + String.valueOf(currentlongi), null);
                    // upload 위도 경도
                }

                String http2 = requestHttpURLConnection.request(url, values); // 해당 URL로 부터 결과물을 얻어온다. [{u'fire': None}]
                http2 = http2.substring(1, http2.length() - 1); // 대괄호 삭제 {u'fire': '0'}
                http2 = http2.replaceAll("u'", "'"); // u' -> ' {'fire': '0'}
                http2 = http2.replaceAll("'", "\""); // ' -> " {"fire": "0"}
                http2 = http2.substring(0, http2.length() - 1); // {"fire": "0"
                http2 = http2 + ",";

                String http3 = requestHttpURLConnection.request(url2, values); // 해당 URL로 부터 결과물을 얻어온다.
                //[{u'longi': u'126.6572333', u'lati': u'37.4508218'}]
                http3 = http3.substring(1, http3.length() - 1);//{u'longi': u'126.6572333', u'lati': u'37.4508218'}
                http3 = http3.replaceAll("u'", "'"); //{'longi': 126.6572333', 'lati': '37.4508218'}
                http3 = http3.replaceAll("'", "\""); //{"longi": "126.6572333", "lati": "37.4508218"}
                http3 = http3.substring(1, http3.length()); // "longi": "126.6572333", "lati": "37.4508218"}

                http2 = http2 + http3; //{"fire": "0", "longi": "126.6572333", "lati": "37.4508218"}
                Log.i("loghttp", http2);
                try {
                    result = (JSONObject) parser.parse(http2); // 문자열 json parsing
                    return result;
                } catch (ParseException e) {
                    Log.i("logparse", "pasing error");
                }
                return null;
            } catch (NullPointerException e) {
                Log.i("loghttp", "http error");
                return null;
            }
        }

        @Override
        protected void onPostExecute(JSONObject s) { // doInBackground return 값 s
            super.onPostExecute(s);

            if (s == null) { // 받아온 정보가 없을 때
                explain.setText("");
                address.setText("");
                httpfire.setText("");
                phonegps.setText("                        서버를 켜주세요!");
                return;
            }

            explain.setText("     \u003C 현재 Thinkar 위치 \u003E");
            phonegps.setText("위도: " + s.get("lati") + "        경도:" + s.get("longi"));

            latitu = Double.parseDouble(s.get("lati").toString());
            longitu = Double.parseDouble(s.get("longi").toString());

            String A = s.get("lati").toString();
            String B = s.get("longi").toString();
            String C = s.get("fire").toString();
            double AA = Double.parseDouble(A);
            double BB = Double.parseDouble(B);

            if (getAddress(MainActivity.this, AA, BB).equals("현재 위치를 확인 할 수 없습니다.")) {
                address.setText(getAddress(MainActivity.this, AA, BB));
            } else {
                address.setText(getAddress(MainActivity.this, AA, BB) + " 에"); // 위도,경도로 주소 얻어서 보여주기;
            }

            if (C.equals("1")) { // 차량에서 화재를 인식하였을 때
                httpfire.setText("화재가 났어요!");
            } else if (C.equals("0")) { // 차량에서 화재를 인식하지 않았을 때
                httpfire.setText("화재가 없어요!");
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) { // permission check
        if (requestCode == PERMISSIONS_ACCESS_FINE_LOCATION
                && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            isAccessFineLocation = true;

        } else if (requestCode == PERMISSIONS_ACCESS_COARSE_LOCATION
                && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            isAccessCoarseLocation = true;
        }

        if (isAccessFineLocation && isAccessCoarseLocation) {
            isPermission = true;
        }
    }

    public static String getAddress(Context mContext, double lat, double lng) { //위도,경도로 주소구하기
        String nowAddress = "현재 위치를 확인 할 수 없습니다.";
        Geocoder geocoder = new Geocoder(mContext, Locale.KOREA);
        List<Address> address;
        try {
            if (geocoder != null) {
                //세번째 파라미터는 좌표에 대해 주소를 리턴 받는 갯수로
                //한좌표에 대해 두개이상의 이름이 존재할수있기에 주소배열을 리턴받기 위해 최대갯수 설정
                address = geocoder.getFromLocation(lat, lng, 1);

                if (address != null && address.size() > 0) {
                    // 주소 받아오기
                    String currentLocationAddress = address.get(0).getAddressLine(0).toString();
                    nowAddress = currentLocationAddress;
                }
            }

        } catch (IOException e) {
            Toast.makeText(mContext, "주소를 가져 올 수 없습니다.", Toast.LENGTH_LONG).show();
            e.printStackTrace();
        }
        return nowAddress;
    }

    public String getDeviceId() // 장치 아이디 얻기
    {

        TelephonyManager mgr = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);

        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE) != PackageManager.PERMISSION_GRANTED) { // permssion check
            return null;
        }else {
            return mgr.getDeviceId();
        }
    }

}