import 'package:flutter/material.dart';

class LogIn extends StatelessWidget {
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
            style: ElevatedButton.styleFrom(
              
              minimumSize: Size(200,50)
            ),
              onPressed: () => {print('clicked')},
              icon: Icon(
                Icons.email,
              ),
              label: Text('Login')),
              
        ],
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
      ),
    ));
  }
}
