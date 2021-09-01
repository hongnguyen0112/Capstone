import 'package:flutter/material.dart';
import 'package:ui/services/auth.dart';

class LogIn extends StatelessWidget {
  final AuthServices _auth = AuthServices();
  bool status = AuthServices().isSignedIn();
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
          SizedBox(height: 20.0),
          Container(
            width: 300,
            child:
            Column(children: [
            TextFormField(
            decoration: InputDecoration(border: OutlineInputBorder(),labelText: "Email",hintText: 'example@intel.com'),
            onChanged: (val) {},
            keyboardType: TextInputType.emailAddress,
          ),
          SizedBox(
            height: 20,
          ),
          TextFormField(
            onChanged: (val) {},
            obscureText: true,
            decoration: InputDecoration(border: OutlineInputBorder(),labelText: "Password"),
            
            
          )],)),
          SizedBox(
            height: 20.0,
          ),
          ElevatedButton(
              style: ElevatedButton.styleFrom(minimumSize: Size(200, 50)),
              onPressed: () async {
                print('clicked');
              },
              child: Text('Login')),
        ],
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
      ),
    ));
  }
}
