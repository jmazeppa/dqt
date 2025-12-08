# site

## prod
https://sites.google.com/view/dqtmazeppa/

## staging (here)
[./arenor.html](https://jmazeppa.github.io/dqt/arenor.html)

## status.json
1. ゲーム内のモンスター図鑑を使う、その数字は完凸かつパネルや開花込み
2. base_status_at_max_levelを出す、小数点以下切り上げ RoundUp (図鑑数字 / 1.25) - 覚醒やパネル数字（ステ倍率は別考慮
3. 覚醒分のステータスをlevelごとに累積で出す、カミュやテリーの完凸はここのlevel5 で対応
4. 才能開花やパネルの数字は別で入れる（これは実際にパネルを見ないとダメ）
5. メモ：そのうちタイプによる最速すばや差とか極み覚醒バッジとか考慮に入れないと入れなくなる
```
[
  {
    "id": 389,
    "name_jp": "キラーマシン3",
    "family_jp": "物質",
    "base_status_at_max_level": [938, 338, 460, 394, 406, 101],
    "panel_status_at_max_level": [150, 30, 15, 25, 15, 15],
    "awakening_table": [
      { "level": 0, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [0, 0, 0, 0, 0, 0] },
      { "level": 1, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [5, 5, 5, 5, 5, 5] },
      { "level": 2, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [10, 10, 10, 10, 10, 10] },
      { "level": 3, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [15, 15, 15, 15, 15, 15] },
      { "level": 4, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [20, 20, 20, 20, 20, 20] },
      { "level": 5, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [25, 25, 25, 25, 25, 25] }
    ]
  },
  {
    "id": 353,
    "name_jp": "魔剣士ピサロ",
    "family_jp": "？？？",
    "base_status_at_max_level": [1105, 476, 490, 265, 470, 176],
    "panel_status_at_max_level": [150, 30, 15, 75, 15, 15],
    "awakening_table": [
      { "level": 0, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [0, 0, 0, 0, 0, 0] },
      { "level": 1, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [5, 5, 5, 5, 5, 5] },
      { "level": 2, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [10, 10, 10, 10, 10, 10] },
      { "level": 3, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [15, 15, 15, 15, 15, 15] },
      { "level": 4, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [20, 20, 20, 20, 20, 20] },
      { "level": 5, "additives": [30, 0, 15, 0, 0, 0], "magnifiers": [25, 25, 25, 25, 25, 25] }
    ]
  },
  {
    "id": 802,
    "name_jp": "大勇者アバン",
    "family_jp": "英雄",
    "base_status_at_max_level": [1193, 400, 442, 377, 352, 222],
    "panel_status_at_max_level": [50, 50, 25, 75, 25, 25],
    "awakening_table": [
      { "level": 0, "additives": [0, 0, 15, 0, 20, 0], "magnifiers": [0, 0, 0, 0, 0, 0] },
      { "level": 1, "additives": [0, 0, 15, 0, 20, 0], "magnifiers": [5, 5, 5, 5, 5, 5] },
      { "level": 2, "additives": [0, 0, 15, 0, 20, 0], "magnifiers": [10, 10, 10, 10, 10, 10] },
      { "level": 3, "additives": [0, 0, 15, 0, 20, 0], "magnifiers": [15, 15, 15, 15, 15, 15] },
      { "level": 4, "additives": [0, 0, 15, 0, 20, 0], "magnifiers": [20, 20, 20, 20, 20, 20] },
      { "level": 5, "additives": [0, 0, 15, 0, 20, 0], "magnifiers": [25, 25, 25, 25, 25, 25] }
    ]
  },
]
```
