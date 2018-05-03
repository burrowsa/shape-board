#!/usr/bin/env python
from flask import Flask, send_file, request, redirect, jsonify
from flask_socketio import SocketIO, emit, disconnect
from flask_ask import Ask, statement, session as ask_session, delegate, question
import sys, json
from random import randint, choice


app = Flask(__name__) 
app.config['SECRET_KEY'] = b"SECRET!!!! Shhhhhhh" 
ask = Ask(app, '/alexa')
app.config['ASK_VERIFY_REQUESTS'] = False
socketio = SocketIO(app) 


_shapes = []


@app.route('/')
def index():
  return send_file('index.html')


@app.route('/api/add_shape', methods=['POST'])
def add_shape():
    _shapes.append(request.json)
    broadcast_update()
    return jsonify(_shapes)


@app.route('/api/clear_shapes', methods=['GET'])
def clear_shapes():
    _shapes.clear()
    broadcast_update()
    return jsonify(_shapes)


def create_shape(shape, color):
  new_shape = dict(type=shape, color=color, x=randint(0, 600), y=randint(0, 400))

  if color == 'black':
    new_shape['outline'] = 'white'
  else:
    new_shape['outline'] = 'black'

  if shape == 'circle':
    new_shape['r'] = randint(10, 100)
  elif shape == 'rectangle':
    new_shape['width'] = randint(10, 600)
    new_shape['height'] = randint(10, 400)
  else:
    new_shape['side'] = randint(10, 200)
  
  _shapes.append(new_shape)

  broadcast_update()


def broadcast_update():
  socketio.emit('update', _shapes, broadcast=True, namespace='/v1')


@socketio.on('connect', namespace='/v1')
def v1_connect():
  emit('update', _shapes)


@socketio.on_error('/v1')
def v1_error_handler(e):
  emit('error', "An error occured on {}".format(request.event["message"]))
  print(type(e), file=sys.stderr)
  print(e, file=sys.stderr)


@ask.launch
def launched():
    return question('Welcome to Shape Board')


@ask.intent('AMAZON.StopIntent')
@ask.intent('AMAZON.CancelIntent')
@ask.session_ended
def stop(): 
  return statement("Good bye")


@ask.intent('AMAZON.HelpIntent')
def help(): 
  return question("You can add shapes by saying something like add a red circle or you can say clear the board or you can say exit.")


@ask.intent('ClearShapes')
def alexa_clear_shapes(): 
  clear_shapes()
  return statement(choice([
                          "Cleared",
                          "Done",
                          "Complete",
                          ]))


@ask.intent('AddShape')
def alexa_add_shape(shape, color):
  if ask_session['dialogState'] != 'COMPLETED' or shape is None or color is None:
    return delegate()

  if shape.lower() not in {'circle', 'rectangle', 'triangle', 'square'}:
    return statement("Sorry, I don't know the shape {}".format(shape))

  if color.lower() not in {'red', 'green', 'blue', 'black', 'yellow'}:
    return statement("Sorry, I don't know the color {}".format(color))

  create_shape(shape, color)
    
  return statement(choice([
                          "Added",
                          "Okay",
                          "Done"
                          ]))


if __name__ == '__main__':
  socketio.run(app, debug=True)
