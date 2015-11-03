import sys
import time
from geopy.geocoders import GoogleV3

LIMIT = 2500
call = 0

def file_to_dict(file_obj, delimeter):
  '''
  takes a file object (.tsv) and returns the dataset as a list of dictionary
  '''
  line = file_obj.readline().strip()
  res = []
  keys = []
  if line != '':
    keys = line.split(delimeter)
  if len(keys) == 0:
    print('Invalid input (no column names found).')
    sys.exit(1)
  line = file_obj.readline().strip()
  while line != '':
    vals = line.split(delimeter)
    val_len = len(vals)
    if len(keys) != val_len:
      print('Invalid input (# of columns).')
      sys.exit(1)
    record = {}
    for i in range(val_len):
      record[keys[i]] = vals[i].strip()
    res.append(record)
    line = file_obj.readline().strip()
  print('Read ' + str(len(res)) + ' records from file.')
  return res

def dict_to_file(list_of_dict, file_obj, delimeter):
  '''
  output a list of dictionary as a delimeted data file
  '''
  cnt = 0
  for row in list_of_dict:
    if cnt == 0:
      for key in row.keys():
        if row.keys().index(key) != 0:
          file_obj.write('|')
        file_obj.write(key)
      file_obj.write('\n')
    line = ''
    for key in row.keys():
      if row.keys().index(key) != 0:
        file_obj.write('|')
      file_obj.write(str(row[key]))
    file_obj.write('\n')
    cnt += 1
  file_obj.close()
  print('Wrote ' + str(cnt) + ' records to file.')
  return

def geocode(dataset, geocoder):
  for row in dataset:
    if row['lat'] != 'NA' and row['long'] != 'NA':
      continue
    if '~' in row['address']:
      coord = row['address'].split('~')
      if len(coord) != 2:
        row['lat'] = 'NA'
        row['long'] = 'NA'
      else:
        row['lat'] = coord[0]
        row['long'] = coord[1].split(',')[0]
      row['address'] = row['address'].split(',')[0]
      continue
    # NEED lat and long
    time.sleep(0.2)
    res = get_lat_long(row['address'], geocoder)
    if res == -1:
      print('API Limit reached.')
      return
    elif res:
      row['lat'] = res[1][0]
      row['long'] = res[1][1]
      print(res[1])
    # else:
    #   print('Geocoding failed: ' + row['address'])

def get_lat_long(address, geocoder):
  global call
  global LIMIT
  if call < LIMIT:
    res = geocoder.geocode(address)
    call += 1
    return res
  else:
    return -1

# START
if __name__ == '__main__':
  # INPUT
  if len(sys.argv) < 2:
    print('Please specify the dataset.')
    sys.exit(1)
  f_name = sys.argv[1]
  f = open(f_name, 'r')
  d = file_to_dict(f, '|')
  # GEOCODING # Warning: API limit is strict!
  geocoder = GoogleV3(api_key = 'AIzaSyC2tmJgfw8-hd7-AmFLv_SJjps5p7uyPqA', timeout = 10)
  geocode(d, geocoder)
  # OUTPUT
  of = open('output.txt', 'w')
  dict_to_file(d, of, '|')
# END
