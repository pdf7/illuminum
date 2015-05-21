package com.example.kolja.Illumino;

import android.graphics.Bitmap;
import android.location.Location;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;

/**
 * Created by kolja on 5/1/15.
 */
public class m2m_container {
    public String mid;
    public int state;
    public String area;
    public int detection;
    public Location l;
    public long last_seen;
    public String alias;
    public boolean webcam_on=false;
    public Bitmap last_img=null;

    public TextView stateLabel=null;
    public TextView updateLabel=null;
    public TextView aliasLabel=null;
    public ImageButton onOffButton=null;
    public ImageView webcam_pic=null;



    public m2m_container(){
        super();
    }

    public m2m_container(String mid, int state, String area, int detection, Location l, int last_seen, String alias){
        this.mid=mid;
        this.state=state;
        this.area=area;
        this.detection=detection;
        this.l=l;
        this.last_seen=last_seen;
        this.alias=alias;
    }
}