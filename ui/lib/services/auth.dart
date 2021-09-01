import 'package:firedart/auth/user_gateway.dart';
import 'package:firedart/firedart.dart';

class AuthServices {
  final FirebaseAuth _auth = FirebaseAuth.instance;

  Future signInAnons() async {
    try {
      await _auth.signInAnonymously();
      User user = await FirebaseAuth.instance.getUser();
      return user;
    } catch (e) {
      print(e.toString());
      return null;
    }
  }
}
