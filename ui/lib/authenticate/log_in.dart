import 'package:flutter/material.dart';
import 'package:ui/services/auth.dart';

class LogIn extends StatefulWidget {


  @override
  _LogInState createState() => _LogInState();
}

class _LogInState extends State<LogIn> {
  final AuthServices _auth = AuthServices();

  bool status = AuthServices().isSignedIn();

  String email = '';

  String password = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Intel Virtual Assistant'),
        centerTitle: true,
        backgroundColor: Colors.blue[800],
        actions: [
          TextButton.icon(onPressed: () =>(
           Navigator.pushReplacementNamed(context, '/register')
          ), icon: Icon(Icons.person),label: Text('Sign Up'),style: TextButton.styleFrom(primary: Colors.white, padding: EdgeInsets.symmetric(horizontal: 20)),)
        ],
      ),
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
              child: Column(
                children: [
                  TextFormField(
                    decoration: InputDecoration(
                        border: OutlineInputBorder(),
                        labelText: "Email",
                        hintText: 'example@intel.com',
                        prefixIcon: Icon(Icons.email)),
                    onChanged: (val) {
                      setState(() => email = val);
                    },
                    keyboardType: TextInputType.emailAddress,
                  ),
                  SizedBox(
                    height: 20,
                  ),
                  TextFormField(
                    onChanged: (val) {
                      setState(() => password = val);
                    },
                    obscureText: true,
                    decoration: InputDecoration(
                        border: OutlineInputBorder(),
                        labelText: "Password",
                        prefixIcon: Icon(Icons.lock)),
                  )
                ],
              )),
          SizedBox(
            height: 20.0,
          ),
          ElevatedButton(
              style: ElevatedButton.styleFrom(minimumSize: Size(200, 50)),
              onPressed: () async {
                print(email);
                print(password);
              },
              child: Text('Login')),
        ],
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
      ),
    ));
  }
}
