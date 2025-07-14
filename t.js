var lootManager = (function () {
  "use strict";

  // Название заметки для лута
  const LOOT_JOURNAL_NAME = "###LOOT###";
  const LOOT_JOURNAL_PAGE_NAME = "Лут";

  // CSS для кнопок и сообщений
  const openReport =
    "<div style='text-align: center; display: block; color: #c29748; padding: 5px; border: 2px solid #c29748; background-color: #1e1e1e; border-radius: 10px;'>";
  const closeReport = "</div>";
  const openHeader =
    "<div style='font-weight:bold; background:#404040; color:#c29748; padding:3px; margin-bottom:5px;'>";
  const closeHeader = "</div>";

  function btn(label, cmd) {
    return (
      "<a href='!" +
      cmd +
      "' style='background:#404040; color:#eee; padding:2px 5px; border-radius:5px; text-decoration:none; margin-right:5px;'>" +
      label +
      "</a>"
    );
  }

  // Функция для получения или создания заметки ###LOOT### и её страницы
  function getOrCreateLootJournal() {
    let journal = findObjs({ type: "journal", name: "###LOOT###" })[0];
    if (!journal) {
      // Создание новой заметки
      journal = createObj("journal", {
        name: "###LOOT###",
        inplayerjournals: {}, // Только для ГМа
      });
      log(`Создана новая заметка ${LOOT_JOURNAL_NAME}`);
    }

    // Проверка наличия страницы
    let page = findObjs({
      type: "page",
      _journalid: journal.id,
      name: LOOT_JOURNAL_PAGE_NAME,
    })[0];
    if (!page) {
      // Создание новой страницы в заметке
      page = createObj("page", {
        _journalid: journal.id,
        name: LOOT_JOURNAL_PAGE_NAME,
        archived: false,
      });
      log(
        `Создана новая страница "${LOOT_JOURNAL_PAGE_NAME}" в заметке ${LOOT_JOURNAL_NAME}`
      );
    }

    return { journal: journal, page: page };
  }

  // Функция для раскрытия inline-роллов [[...]]
  function expandInlineRolls(content, inlinerolls) {
    // Обработка $[[...]] роллов
    if (_.has(inlinerolls)) {
      _.each(inlinerolls, function (roll, index) {
        let key = "$[[" + index + "]]";
        let replacement = "";

        if (roll.results.total) {
          replacement = roll.results.total;
        } else if (roll.results.rolls && roll.results.rolls.length > 0) {
          // Обработка таблиц
          let tableItems = [];
          _.each(roll.results.rolls, function (r) {
            if (r.tableItem && r.tableItem.name) {
              tableItems.push(r.tableItem.name);
            }
          });
          replacement = tableItems.join(", ");
        }

        content = content.replace(key, replacement);
      });
    }

    // Обработка [[...]] роллов (inline expressions)
    const inlineRollRegex = /\[\[(.*?)\]\]/g;
    content = content.replace(inlineRollRegex, function (match, p1) {
      // Здесь можно обработать содержимое внутри [[...]], если необходимо
      // В текущем контексте предположим, что они уже раскрыты
      return p1; // Возвращаем содержимое без [[ и ]]
    });

    return content;
  }

  // Функция для извлечения блока description
  function extractDescription(content) {
    const regex = /\{\{description=(.*?)\}\}/s;
    const match = content.match(regex);
    if (match && match[1]) {
      return match[1].trim();
    }
    return "";
  }

  // Функция для парсинга описания в предметы
  function parseDescription(description) {
    // Разделение по строкам или тегам <br/> или \n
    let lines = description.split(/<br\s*\/?>|\r?\n/);
    let items = [];
    lines.forEach((line) => {
      line = line.trim();
      if (line.length === 0) return;
      // Предполагаемый формат: "Название предмета количество фнт"
      let match = line.match(/^(.*)\s+(\d+)\s*фнт$/i);
      if (match) {
        let name = match[1].trim();
        let qty = parseInt(match[2], 10);
        items.push({ name: name, qty: qty });
      }
    });
    return items;
  }

  // Функция для формирования строки лута для команды !takeLoot
  function buildLootString(items) {
    return items.map((item) => `${item.name} ${item.qty} фнт`).join("%%%");
  }

  // Функция для парсинга строки лута из команды !takeLoot
  function parseLootString(lootStr) {
    let items = lootStr.split("%%%");
    let parsed = [];
    items.forEach((itemStr) => {
      itemStr = itemStr.trim();
      if (itemStr.length === 0) return;
      let match = itemStr.match(/^(.*)\s+(\d+)\s*фнт$/i);
      if (match) {
        let name = match[1].trim();
        let qty = parseInt(match[2], 10);
        parsed.push({ name: name, qty: qty });
      }
    });
    return parsed;
  }

  // Функция для получения текущего лута из заметки
  function getCurrentLoot(page) {
    let description = page.get("notes") || "";
    let items = parseDescription(description);
    return items;
  }

  // Функция для обновления лута в заметке
  function updateLoot(page, newItems) {
    let currentItems = getCurrentLoot(page);
    // Создание карты для быстрого поиска
    let itemMap = {};
    currentItems.forEach((item) => {
      itemMap[item.name] = item.qty;
    });
    // Обновление с новыми предметами
    newItems.forEach((item) => {
      if (itemMap.hasOwnProperty(item.name)) {
        itemMap[item.name] += item.qty;
      } else {
        itemMap[item.name] = item.qty;
      }
    });
    // Формирование нового описания
    let newDescription = Object.keys(itemMap)
      .map((name) => `${name} ${itemMap[name]} фнт`)
      .join("\n");
    page.set("notes", newDescription);
  }

  // При запуске скрипта, убедиться, что заметка существует
  on("ready", function () {
    getOrCreateLootJournal();
    log("Скрипт управления лутом готов.");
  });

  // Обработка сообщений в чате
  on("chat:message", function (msg) {
    if (
      msg.type !== "api" &&
      msg.type !== "whisper" &&
      msg.type !== "general"
    ) {
      // Обрабатывать только api, whisper и general сообщения
      return;
    }

    // Проверка наличия ###LOOT### в конце сообщения
    if (msg.content.trim().endsWith("###LOOT###}}")) {
      // Раскрытие inline-роллов
      let expandedContent = expandInlineRolls(msg.content, msg.inlinerolls);

      // Извлечение блока description
      let description = extractDescription(expandedContent);
      if (description.length === 0) {
        sendChat(
          "Loot Manager",
          "Не найден блок {{description=...}} в сообщении."
        );
        return;
      }

      // Парсинг предметов
      let items = parseDescription(description);
      if (items.length === 0) {
        sendChat("Loot Manager", "Нет предметов для лута.");
        return;
      }

      // Формирование строки лута
      let lootStr = buildLootString(items);

      // Формирование команды
      let cmd = `takeLoot "${lootStr}"`;

      // Создание кнопки
      let buttonHtml = btn("ЗАБРАТЬ ЛУТ", cmd);

      // Оборачивание в CSS
      let message =
        openReport +
        openHeader +
        "Лут доступен:" +
        closeHeader +
        buttonHtml +
        closeReport;

      // Отправка сообщения в общий чат
      sendChat("Loot Manager", message);
    }

    // Проверка, является ли сообщение командой !takeLoot
    if (msg.content.startsWith("!takeLoot")) {
      // Извлечение аргументов
      let args = msg.content.match(/^!takeLoot\s+"([^"]+)"$/);
      if (!args || args.length < 2) {
        sendChat(
          "Loot Manager",
          'Неверный формат команды. Используйте: !takeLoot "Предмет1%%%Предмет2%%%Предмет3"'
        );
        return;
      }
      let lootStr = args[1];

      // Парсинг предметов
      let newItems = parseLootString(lootStr);
      if (newItems.length === 0) {
        sendChat("Loot Manager", "Нет валидных предметов для добавления.");
        return;
      }

      // Получение заметки лута
      let { journal, page } = getOrCreateLootJournal();
      if (!journal || !page) {
        sendChat(
          "Loot Manager",
          "Не удалось найти или создать заметку ###LOOT###."
        );
        return;
      }

      // Обновление лута
      updateLoot(page, newItems);

      // Уведомление пользователя
      sendChat("Loot Manager", "Лут успешно обновлён.");
    }
  });

  return {
    // Публичные методы при необходимости
  };
})();
