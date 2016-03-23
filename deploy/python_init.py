import sys
sys.path.append('V:/dev')


try:
  import pipeline.c4d
  print 'SUCCESS  Loaded ESPN c4d pipeline utilities!'

except:
  print 'ERROR  Failed to load ESPN c4d pipeline utilities!'
