import sys
sys.path.append('Y:\\workspace\\scripts\\')


try:
  import pipeline.c4d
  print 'SUCCESS  Loaded ESPN c4d pipeline utilities!'

except:
  print 'ERROR  Failed to load ESPN c4d pipeline utilities!'
