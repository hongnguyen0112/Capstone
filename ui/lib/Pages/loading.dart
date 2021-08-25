import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_spinkit/flutter_spinkit.dart';

class Loading extends StatefulWidget {
  const Loading({Key? key}) : super(key: key);

  @override
  _LoadingState createState() => _LoadingState();
}

class _LoadingState extends State<Loading> {
  String status = "Loading, this may take few seconds..";
  static const String BOT_URL = "http://localhost:5005/webhooks/rest/webhook";
  Map<String, String> requestHeaders = {
    "Content-type": "application/json",
  };

  void getResponse() async {
    http.Client getClient() {
      return http.Client();
    }

    var client = getClient();
    try {
      await client.post(Uri.parse(BOT_URL),
          headers: requestHeaders,
          body: jsonEncode({"sender": 'test', 'message': 'hi'}));
      Navigator.pushNamed(context, '/chat');
    } catch (e) {
      print('caught error:$e');
      setState(() {
        status = "Loading Error...";
      });
    }
  }

  void initState() {
    super.initState();
    getResponse();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        backgroundColor: Colors.blue[900],
        body: Center(
            child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SpinKitWave(color: Colors.white, size: 50.0),
            SizedBox(
              height: 20.0,
            ),
            Text(
              status,
              style: TextStyle(fontSize: 20.0, color: Colors.white),
            ),
             SizedBox(
              height: 20.0,
            ),
            TextButton.icon(
                onPressed: () {
                  getResponse();
                },
                icon: Icon(Icons.autorenew, color: Colors.white),
                label: Text('Try again',
                style: TextStyle( color: Colors.white)))
          ],
        )));
  }
}
//Add I button in case there is an error