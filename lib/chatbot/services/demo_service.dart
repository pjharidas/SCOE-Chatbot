import 'dart:convert';
import 'dart:math';
import "package:http/http.dart" as http;

List<String> demoBotReplies = [
  'Hello! How can I help you?',
  'I am a bot. I can help you with your queries.',
  'I am good, How Are you?',
  "Alright! Let's do that..."
];

String returnBotReply() {
  Random random = Random();
  int randomNumber = random.nextInt(demoBotReplies.length);
  return demoBotReplies[randomNumber];
}

String BASE_URL = "http://192.168.1.6:5000";
// String BASE_URL = "";

// write a function to get the response from the server
Future<String> getResponse(String message) async {
  var response = await http.post(Uri.parse("$BASE_URL/chat"),
      headers: {"Content-Type": "application/json"},
      body: '{"message": "$message"}');
  if (response.statusCode == 200) {
    Map<String, dynamic> responseData = jsonDecode(response.body);
    return responseData['response'] ?? 'No response found';
  } else {
    throw Exception('Failed to get response from server');
  }
}
