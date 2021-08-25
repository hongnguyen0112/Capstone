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
  String error = "Loading..";
  static const String BOT_URL =
      "http://localhost:5005/webhooks/rest/webhook";
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
        error = "Loading Error...";
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
            child: SpinKitWave(
          color: Colors.white,
          size: 50.0,
        )));
  }
}
