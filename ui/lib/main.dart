import 'package:flutter/material.dart';

import 'package:ui/screens/loading.dart';
import 'package:ui/authenticate/log_in.dart';
import 'package:ui/authenticate/sign_up.dart';
import 'screens/home_screen.dart';
import 'package:firedart/firedart.dart';

Future main() async {
  FirebaseAuth.initialize('AIzaSyARw0GgR7bfrK8d0O2Yy4un3W1MN25_EFc',VolatileStore());
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
        '/register':(context) => SignUp(),
        '/loading':(context) => Loading(),
        '/chat':(context) => HomeScreen(),
        

      },
    );
  }
}
