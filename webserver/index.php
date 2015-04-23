<?php
///////////////// server status ///////////////////////////
$body='<h1 id="l10n_title">Python WebSocket-Server<br>Status: ';
unset($output);
exec('ps -ax|grep "python3" | grep "main.py"| grep -v "grep"',$output,$return_var);
if(!empty($output[0])){	// python serer is running add everything
	$body.='<font color="green">online</font>';

	$body.='</h1>';
	// add ws display stuff
	$extra_header='<script type="text/javascript">
		var con = null;
		function start() {
		        con = new WebSocket(\'ws://192.168.1.80:9876/\');
			con.onopen = function(){
				login("kolja","huhu");
			};
			// reacting on incoming messages
		        con.onmessage = function(msg) {
                		console.log("Message");
				msg_dec=JSON.parse(msg.data);
				console.log(msg_dec);

				if(msg_dec["cmd"]=="m2v_login"){
					if(document.getElementById("clients")!=undefined){
						var area=document.getElementById(msg_dec["account"]+"_"+msg_dec["area"]);
						if(area==undefined){
							var node=document.createElement("P");
							node.appendChild(document.createTextNode("Area:"+msg_dec["account"]+"_"+msg_dec["area"]+""));
							node.setAttribute("id",msg_dec["account"]+"_"+msg_dec["area"]);

							var button=document.createElement("A");
							button.setAttribute("id",+msg_dec["account"]+"_"+msg_dec["area"]+"_on");
							button.onclick=function(){
								var msg_int=msg_dec;
								return function(){
									set_detection(msg_int["account"],msg_int["area"],1);
								}
							   }();
							button.className="button";
							button.text="Detection on";
							node.appendChild(button);

							button=document.createElement("A");
							button.setAttribute("id",+msg_dec["account"]+"_"+msg_dec["area"]+"_off");
							button.onclick=function(){
								var msg_int=msg_dec;
								return function(){
									set_detection(msg_int["account"],msg_int["area"],0);
								}
							   }();
							button.className="button";
							button.text="Detection off";
							node.appendChild(button);

							document.getElementById("clients").appendChild(node);
							area=node;
						}

						var node=document.createElement("P");
						node.appendChild(document.createTextNode("client:"+msg_dec["mid"]));

						var sub_node=document.createElement("P");
						sub_node.setAttribute("id",msg_dec["mid"]+"_hb");
						node.appendChild(sub_node);

						sub_node=document.createElement("P");
						sub_node.setAttribute("id",msg_dec["mid"]+"_state");
						node.appendChild(sub_node);

						sub_node=document.createElement("img");
						sub_node.setAttribute("id",msg_dec["mid"]+"_img");
						node.appendChild(sub_node);
						console.log(msg_dec["mid"]+"_img"+" angelegt");


						area.appendChild(node);
						console.log("hb feld in client angebaut");

						document.getElementById(msg_dec["mid"]+"_state").innerHTML=msg_dec["state"];
					}
				}

				else if(msg_dec["cmd"]=="hb"){
					if(document.getElementById(msg_dec["mid"]+"_hb")!=undefined){
						document.getElementById(msg_dec["mid"]+"_hb").innerHTML=msg_dec["ts"];
						console.log("hb ts updated");
					}
				}

				else if(msg_dec["cmd"]=="state_change"){
					e=document.getElementById(msg_dec["mid"]+"_state");
					state=msg_dec["state"];
					if(e!=undefined){
						if(state==0){
							e.innerHTML="Idle";
							img=document.getElementById(msg_dec["mid"]+"_img");
							if(img!=undefined){
								console.log("habs");
								img.src="";
							}
						} else if(state==1){
							e.innerHTML="Alert";
						} else if(state==2){
							e.innerHTML="Detection offline";
						}
					}
				}

				else if(msg_dec["cmd"]=="rf"){
					console.log("suche nach: "+msg_dec["mid"]+"_img");
					img=document.getElementById(msg_dec["mid"]+"_img");
					if(img!=undefined){
						console.log("habs");
						img.src="http://192.168.1.80/"+msg_dec["path"];
					};
				}

			}

	        }
		function login(user,pw) {
			console.log("send login");
			if(con == null){
				return;
			}
			var cmd_data = { "cmd":"login", "login":user, "pw":pw};
			console.log(JSON.stringify(cmd_data));
			con.send(JSON.stringify(cmd_data));
		}

		function set_detection(user,area,on_off){
			if(con == null) {
				return;
			}
			var cmd_data = { "cmd":"detection", "state":on_off, "area":area, "user":user};
			console.log(JSON.stringify(cmd_data));
			con.send(JSON.stringify(cmd_data));
		}

		function send(app,cmd) {
			console.log("send");
			console.log("app:"+app);
			console.log("cmd:"+cmd);
			if(con == null) {
				return;
			}
	
			var cmd_data = { "cmd":cmd, "app":app};
			console.log(JSON.stringify(cmd_data));
			con.send(JSON.stringify(cmd_data));
		}
		</script>';
	$body.='<br>';
	
	// add webcam stuff
	//$body.='<h1 id="l10n_title">WebCam-Server';
	//$body.='<div id="webcam_status">Status: -</div>';
	//$body.='<dir id="webcam_pic"></div>';
	//$body.='</h1>';
	$body.='<h1 id="l10n_title">Clients</h1>';
	$body.='<div id="clients"></div>';

	// add reboot button
	//$body.='<h1 id="l10n_title">Controll</h1>';
	//$body.='<a class="button" id="detection_start" onclick="send(\'detection\',\'on\')">Detection on</a>';
	//$body.='<a class="button" id="detection_stop" onclick="send(\'detection\',\'off\')">Detection off</a>';
	
} else { //python server is not running just add start button
	$body.='<font color="red">offline</font> &nbsp; ';
	#$body.='<a class="button" href="http://'.$_SERVER[HTTP_HOST].$_SERVER[REQUEST_URI].'?start_python">Start server</a>';
}

///////////////// server status ///////////////////////////

///////////////// header ///////////////////////////
$header='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"><head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta http-equiv="x-dns-prefetch-control" content="off">
        <meta name="robots" content="noindex">
        <link rel="stylesheet" href="status_blue.css" type="text/css" media="screen" charset="utf-8">
        <title></title>
	'.$extra_header.'
    </head>
    <body onload="start()">
        <table height="100%" width="100%">
            <tbody><tr>
                <td align="center" valign="middle">';
$footer='</td></tr></tbody></table></body></html>';
///////////////// header ///////////////////////////
echo $header;
echo $body;
echo $footer;
?>
