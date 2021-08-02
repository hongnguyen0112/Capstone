import 'package:bubble/bubble.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  //Properties and Variables
  final GlobalKey<AnimatedListState> _listKey = GlobalKey();
  List<String> _data = [];
  static const String BOT_URL = "http://localhost:5005/webhooks/rest/webhook";
  TextEditingController queryController = TextEditingController();
  Map<String, String> requestHeaders = {
    "Content-type": "application/json",
  };
  ScrollController _scrollController = new ScrollController();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Intel Virtual Assistant'),
        centerTitle: true,
        backgroundColor: Colors.blue[800],
      ),
      body: Stack(
        children: [
          AnimatedList(
              key: _listKey,
              initialItemCount: _data.length,
              itemBuilder: (BuildContext context, int index,
                  Animation<double> animation) {
                return buildItem(_data[index], animation, index);
              }),
          Align(
              alignment: Alignment.bottomCenter,
              child: ColorFiltered(
                  colorFilter: ColorFilter.linearToSrgbGamma(),
                  child: Container(
                    color: Colors.white,
                    child: Padding(
                        padding: EdgeInsets.only(left: 20, right: 20),
                        child: TextField(
                          style: TextStyle(color: Colors.black),
                          decoration: InputDecoration(
                            icon: Icon(
                              Icons.message,
                              color: Colors.blue[800],
                            ),
                            hintText: "Say Hi!",
                            fillColor: Colors.white12,
                          ),
                          controller: queryController,
                          textInputAction: TextInputAction.send,
                          onSubmitted: (msg) {
                            this.getResponse();
                          },
                        )),
                  )))
        ],
      ),
    );
  }

//client
  // response function
  void getResponse() async {
    if (queryController.text.length > 0) {
      this.insertSingleItem(queryController.text);
      var client = getClient();
      try {
        client.post(Uri.parse(BOT_URL),
            headers: requestHeaders,
            body:
                jsonEncode({"sender": 'test', 'message': queryController.text}))
          ..then((response) {
            List<dynamic> data = jsonDecode(response.body);
            Map messageData = data[0];
            // if the size of the list is less then 1 then insert only one item
            if (data.length <= 1) {
              insertSingleItem(messageData['text'] + '<bot>');
            }
            // else insert all the items
            else {
              String message = '';
              data.forEach((e) => {message += (e['text'] + "\n")});
              insertSingleItem(message + '<bot>');
            }
          });
      } catch (e) {
        print(e);
        return null;
      } finally {
        client.close();
        queryController.clear();
      }
    }
  }

  void insertSingleItem(String message) {
    _data.add(message);
    _listKey.currentState?.insertItem(_data.length - 1);
  }

  http.Client getClient() {
    return http.Client();
  }
}

Widget buildItem(String item, Animation<double> animation, int index) {
  bool mine = item.endsWith("<bot>");
  return SizeTransition(
    sizeFactor: animation,
    child: Padding(
      padding: EdgeInsets.only(top: 10),
      child: Container(
        alignment: mine ? Alignment.topLeft : Alignment.topRight,
        child: Bubble(
          child: Text(
            item.replaceAll("<bot>", ""),
            style: TextStyle(
              color: mine ? Colors.white : Colors.black,
            ),
          ),
          color: mine ? Colors.blue : Colors.grey[200],
          padding: BubbleEdges.all(10),
        ),
      ),
    ),
  );
}
