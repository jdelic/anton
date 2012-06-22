import random
import match

@match.command("!zalgo")
def zalgo_cmd(callback, message):
  return zalgo(message)

# data set of leet unicode chars
#---------------------------------------------------
#those go UP
zalgo_up = [
        u"\u030d",       u"\u030e",       u"\u0304",      u"\u0305",
        u"\u033f",       u"\u0311",       u"\u0306",      u"\u0310",
        u"\u0352",       u"\u0357",       u"\u0351",      u"\u0307",
        u"\u0308",       u"\u030a",       u"\u0342",      u"\u0343",
        u"\u0344",       u"\u034a",       u"\u034b",      u"\u034c",
        u"\u0303",       u"\u0302",       u"\u030c",      u"\u0350",
        u"\u0300",       u"\u0301",       u"\u030b",      u"\u030f",
        u"\u0312",       u"\u0313",       u"\u0314",      u"\u033d",
        u"\u0309",       u"\u0363",       u"\u0364",      u"\u0365",
        u"\u0366",       u"\u0367",       u"\u0368",      u"\u0369",
        u"\u036a",       u"\u036b",       u"\u036c",      u"\u036d",
        u"\u036e",       u"\u036f",       u"\u033e",      u"\u035b",
        u"\u0346",       u"\u031a"
];

#those go DOWN
zalgo_down = [
        u"\u0316",     u"\u0317",       u"\u0318",       u"\u0319",
        u"\u031c",     u"\u031d",       u"\u031e",       u"\u031f",
        u"\u0320",     u"\u0324",       u"\u0325",       u"\u0326",
        u"\u0329",     u"\u032a",       u"\u032b",       u"\u032c",
        u"\u032d",     u"\u032e",       u"\u032f",       u"\u0330",
        u"\u0331",     u"\u0332",       u"\u0333",       u"\u0339",
        u"\u033a",     u"\u033b",       u"\u033c",       u"\u0345",
        u"\u0347",     u"\u0348",       u"\u0349",       u"\u034d",
        u"\u034e",     u"\u0353",       u"\u0354",       u"\u0355",
        u"\u0356",     u"\u0359",       u"\u035a",       u"\u0323"
    ];

#those always stay in the middle
zalgo_mid = [
        u"\u0315",     u"\u031b",       u"\u0340",      u"\u0341",
        u"\u0358",     u"\u0321",       u"\u0322",      u"\u0327",
        u"\u0328",     u"\u0334",       u"\u0335",      u"\u0336",
        u"\u034f",     u"\u035c",       u"\u035d",      u"\u035e",
        u"\u035f",     u"\u0360",       u"\u0362",      u"\u0338",
        u"\u0337",     u"\u0361",       u"\u0489"
    ];

def is_zalgo_char(c):
  return c in zalgo_up or c in zalgo_down or c in zalgo_mid

def zalgo(text, mode=0, up=True, mid=True, down=True):
  def fn():
    for c in text:
      if is_zalgo_char(c):
        continue

      yield c

      if mode == 0:
        num_up = random.randint(0, 8)
        num_mid = random.randint(0, 2)
        num_down = random.randint(0, 8)
      elif mode == 1:
        num_up = random.randint(0, 8) + 1
        num_mid = random.randint(0, 3)
        num_down = random.randint(0, 8) + 1
      else:
        num_up = random.randint(0, 16) + 3
        num_mid = random.randint(0, 4) + 1
        num_down = random.randint(0, 16) + 3

      if up:
        for x in range(num_up):
          yield random.choice(zalgo_up)
      if mid:
        for x in range(num_mid):
          yield random.choice(zalgo_mid)
      if down:
        for x in range(num_down):
          yield random.choice(zalgo_down)

  return "".join(fn())

if __name__ == "__main__":
  import sys
  print zalgo(sys.argv[1], mode=2)

