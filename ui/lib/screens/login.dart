import 'package:flutter/material.dart';
import 'package:firedart/auth/user_gateway.dart';
import 'package:ui/services/auth.dart';

class LogIn extends StatelessWidget {
  final AuthServices _auth = AuthServices();
  @override
  Widget build(BuildContext context) {
    return Scaffold(
        body: Container(
      child: Column(
        children: [
          Center(
              child: Image(
                  image: AssetImage('assets/intel.png'),
                  width: 200,
                  height: 200)),
          ElevatedButton.icon(
              style: ElevatedButton.styleFrom(minimumSize: Size(200, 50)),
              onPressed: () => {print('clicked')},
              icon: Icon(
                Icons.email,
              ),
              label: Text('Login')),
          SizedBox(
            height: 20.0,
          ),
          ElevatedButton.icon(
              style: ElevatedButton.styleFrom(minimumSize: Size(200, 50)),
              onPressed: () async {
                var result = await _auth.signInAnons();
                if (result == null) {
                  print('error');
                } else {
                  print('signIn');
                  print(result);
                }
              },
              icon: Icon(
                Icons.email,
              ),
              label: Text('Login Anonusmouly')),
        ],
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
      ),
    ));
  }
}
