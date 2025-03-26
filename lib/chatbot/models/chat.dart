enum ChatterType { bot, user }

class Chat {
  final ChatterType type;
  final String message;
  const Chat({required this.type, required this.message});
}
