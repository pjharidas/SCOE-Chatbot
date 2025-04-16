import 'dart:math';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sgce_college_predictor/chatbot/models/chat.dart';

class ChatMessagesProvider extends StateNotifier<List<Chat>> {
  ChatMessagesProvider(super.state);
  
  void addMessage(Chat message) {
    state = [...state, message];
  }
}

final chatMessagesProvider =
    StateNotifierProvider<ChatMessagesProvider, List<Chat>>((ref) {
  final greetings = [
    'Hello! How can I assist you today?',
    'Hi there! What can I help you with?',
    'Greetings! How may I be of service?',
    'Hey! What brings you here?',
    'Welcome! Ask me anything.',
    'Hello! Ready to chat?',
    'Hi! How can I help you find the right college?',
    'Good day! What information are you looking for?',
    'Hey there! Let\'s talk colleges.',
    'Welcome! How can I guide you through college prediction?',
  ];
  final initialMessage = greetings[Random().nextInt(greetings.length)];
  return ChatMessagesProvider([Chat(message: initialMessage, type: ChatterType.bot)]);
});
