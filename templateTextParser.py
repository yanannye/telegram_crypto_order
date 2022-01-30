def templateTextParser(inputString,definedFormat):
    maxLen = max(len(inputString), len(definedFormat))
    currLen_inputString = 0
    currLen_definedFormat = 0
    output_Dict = {}

    def getStringIntCurlyBracketsCounter_compare_TWO_element(tmp_inputString, tmp_definedFormat):
        stringAfterRightCurlyBracketsCounter = tmp_definedFormat[tmp_definedFormat.find("}}") + 2:][0:1]
        if (stringAfterRightCurlyBracketsCounter != ''):
            target_inputString = tmp_inputString[:tmp_inputString.find(stringAfterRightCurlyBracketsCounter)]
            target_definedFormat = tmp_definedFormat[2:tmp_definedFormat.find("}}")]
        else:
            target_inputString = tmp_inputString
            target_definedFormat = tmp_definedFormat[2:tmp_definedFormat.find("}}")]

        return target_inputString, target_definedFormat

    def getStringIntCurlyBracketsCounter_compare_ONE_element(tmp_inputString, tmp_definedFormat):
        stringAfterRightCurlyBracketsCounter = tmp_definedFormat[tmp_definedFormat.find("}}") + 2:][0]
        if (stringAfterRightCurlyBracketsCounter != ''):
            target_inputString = tmp_inputString[:tmp_inputString.find(stringAfterRightCurlyBracketsCounter)]
            target_definedFormat = tmp_definedFormat[2:tmp_definedFormat.find("}}")]
        else:
            target_inputString = tmp_inputString
            target_definedFormat = tmp_definedFormat[2:tmp_definedFormat.find("}}")]
        return target_inputString, target_definedFormat

    def getStringBeforeLeftCurlyBracketsCounter(tmp_inputString, tmp_definedFormat):
        target_definedFormat = tmp_definedFormat[:tmp_definedFormat.find('{{')]
        if target_definedFormat == '':
            #  tmp_definedFormat='{{waitTime}});'
            target_inputString = ''
        elif len(target_definedFormat) == 1:
            target_inputString = tmp_inputString[
                                 :tmp_inputString.find(target_definedFormat[-1:]) + 1]  # 比對 "{{"的 前兩個字元要完全一樣
        elif len(target_definedFormat) > 6:
            target_inputString = tmp_inputString[
                                 :tmp_inputString.find(target_definedFormat[-6:]) + 6]  # 比對 "{{"的 前兩個字元要完全一樣
        else:
            target_inputString = tmp_inputString[
                                 :tmp_inputString.find(target_definedFormat[-2:]) + 2]  # 比對 "{{"的 前兩個字元要完全一樣
            if len(target_inputString) == 1:
                target_inputString = "*PARSER ERROR"

        return target_inputString, target_definedFormat

    for i in range(maxLen):
        meta_inputString = inputString[currLen_inputString:]
        meta_definedFormat = definedFormat[currLen_definedFormat:]

        if '{{' in meta_definedFormat:
            # Ignore the elements before "{{"
            ignore_inputString, ignore_definedFormat = getStringBeforeLeftCurlyBracketsCounter(meta_inputString,
                                                                                               meta_definedFormat)
            if ignore_inputString == '*PARSER ERROR':
                output_Dict[ignore_inputString] = ignore_inputString
                break

            currLen_inputString = currLen_inputString + len(ignore_inputString)
            currLen_definedFormat = currLen_definedFormat + len(ignore_definedFormat)
            meta_inputString = inputString[currLen_inputString:]
            meta_definedFormat = definedFormat[currLen_definedFormat:]

            if meta_definedFormat[2:].find("{{") - meta_definedFormat[2:].find("}}") == 3:
                # Get the elements in "{{  }}"  判斷後面一個字元是否符合條件
                target_inputString, target_definedFormat = getStringIntCurlyBracketsCounter_compare_ONE_element(
                    meta_inputString,
                    meta_definedFormat)
            else:
                # Get the elements in "{{  }}"  判斷後面兩個字元是否符合條件
                target_inputString, target_definedFormat = getStringIntCurlyBracketsCounter_compare_TWO_element(
                    meta_inputString,
                    meta_definedFormat)
            output_Dict[target_definedFormat] = target_inputString
            currLen_inputString = currLen_inputString + len(target_inputString)
            currLen_definedFormat = currLen_definedFormat + len(target_definedFormat) + 4
        else:
            break
    return output_Dict