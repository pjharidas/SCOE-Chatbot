import 'dart:math';

List<String> demoBotReplies = [
  'Hello! How can I help you?',
  'I am a bot. I can help you with your queries.',
  'I am good, How Are you?',
  "Alright! Let's do that..."
  ];

  String returnBotReply(){
    Random random = Random();
    int randomNumber = random.nextInt(demoBotReplies.length);
    return demoBotReplies[randomNumber];
  }
  