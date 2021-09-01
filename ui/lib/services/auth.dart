import 'package:firedart/auth/user_gateway.dart';
import 'package:firedart/firedart.dart';
import 'package:ui/models/intel_user.dart';

class AuthServices {
  final FirebaseAuth _auth = FirebaseAuth.instance;

  IntelUser _userFromFirebaseUser(User user) {
    return IntelUser(uid: user.id);
  }

  Future signIn(email, password) async {
    try {
      await _auth.signIn(email, password);
      User user = await _auth.getUser();
      return _userFromFirebaseUser(user);
    } catch (e) {
      print(e.toString());
      return null;
    }
  }

  bool isSignedIn() {
    return _auth.isSignedIn;

  }

  Future signInAnons() async {
    try {
      await _auth.signInAnonymously();
      User user = await FirebaseAuth.instance.getUser();
      print(_auth);
      return _userFromFirebaseUser(user);
    } catch (e) {
      print(e.toString());
      return null;
    }
  }
}
