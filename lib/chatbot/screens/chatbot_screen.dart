import 'dart:developer';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sgce_college_predictor/chatbot/models/chat.dart';
import 'package:sgce_college_predictor/chatbot/providers/demo_provider.dart';
import 'package:sgce_college_predictor/chatbot/services/demo_service.dart';
import 'package:sgce_college_predictor/chatbot/widgets/chat_bubble.dart';

class ChatbotScreen extends ConsumerWidget {
  const ChatbotScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ChatMessagesProvider chatMessagesPro =
        ref.read(chatMessagesProvider.notifier);
    final List<Chat> chatMessages = ref.watch(chatMessagesProvider);
    final TextEditingController chatBoxCtrl = TextEditingController();
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Flex(
          direction: Axis.horizontal,
          children: [
            Flexible(
                child: Column(
              children: [
                Image.asset(
                  'assets/images/logo.png',
                  height: 100,
                  width: 100,
                ),
                const Text(
                  'Chat History',
                  style: TextStyle(fontSize: 15),
                ),
                ListTile(
                  tileColor: Colors.grey[200],
                  title: const Text('Chat 1'),
                  subtitle: const Text('This is the first chat'),
                ),
              ],
            )),
            Flexible(
              flex: 4,
              child: Column(
                spacing: 30,
                // reverse: true,
                children: [
                    Expanded(
                      child: Align(
                      alignment: Alignment.bottomCenter,
                      child: ListView.builder(
                        shrinkWrap: true,
                        itemCount: chatMessages.length,
                        itemBuilder: (context, index) {
                        return ChatBubble(
                          isBot: chatMessages[index].type == ChatterType.bot,
                          message: chatMessages[index].message,
                        );
                        },
                      ),
                      ),
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: MediaQuery.of(context).size.width * 0.60,
                          child: TextField(
                            controller: chatBoxCtrl,
                            onSubmitted: (value) {
                              submitChat(chatMessagesPro, chatBoxCtrl);
                            },
                            enableInteractiveSelection: true,
                            decoration: const InputDecoration(
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.all(Radius.circular(30)),
                              ),
                              hintText: 'Type your message here',
                            ),
                          ),
                        ),
                        IconButton(
                          onPressed: () {
                            submitChat(chatMessagesPro, chatBoxCtrl);
                          },
                          icon: const Icon(Icons.send),
                        ),
                      ],
                    )
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void submitChat(
      ChatMessagesProvider chatMessagesPro, TextEditingController chatBoxCtrl) {
    log("Adding the message to the chat");
    chatMessagesPro.addMessage(Chat(
      message: chatBoxCtrl.text,
      type: ChatterType.user,
    ));
    Chat reply = Chat(
      message: returnBotReply(),
      type: ChatterType.bot,
    );
    chatMessagesPro.addMessage(reply);
    chatBoxCtrl.clear();
  }
}
