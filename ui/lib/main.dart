import 'package:flutter/material.dart';
import 'package:ui/loading.dart';
import 'package:ui/login.dart';
import 'home_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Intel Chatbot",
      initialRoute: '/',
      routes: {
        '/':(context) => LogIn(),
        '/loading':(context) => Loading(),
        '/chat':(context) => HomeScreen(),
        

      },
    );
  }
}
