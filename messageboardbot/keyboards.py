from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply

keyboards = {
	'start': ReplyKeyboardMarkup(keyboard=[['List Channels']]),
	'chosenchannel': ReplyKeyboardMarkup(keyboard = [['📝 Post 📝','List Channels']])
}