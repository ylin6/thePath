#Gerard Martinez, Yucheng Lin, and Marshall Sprigg
#Class for sending player data between the clients

class PlayerMessage:
	def __init__(self, xcoord, ycoord, img):
		self.xPos = xcoord
		self.yPos = ycoord
		self.image = img
