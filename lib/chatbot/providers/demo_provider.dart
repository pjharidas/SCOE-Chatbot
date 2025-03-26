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
  return ChatMessagesProvider([Chat(message: 'Hello, How Can I help you?', type: ChatterType.bot)]);
});
